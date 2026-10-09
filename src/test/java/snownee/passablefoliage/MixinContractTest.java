package snownee.passablefoliage;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import com.google.gson.JsonParser;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.Type;
import org.objectweb.asm.tree.AnnotationNode;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.MethodNode;

/** Checks declared injection signatures without loading Minecraft or applying mixins. */
public final class MixinContractTest {
    private MixinContractTest() { }

    private static ClassNode read(String name) throws IOException {
        try (InputStream input = MixinContractTest.class.getClassLoader().getResourceAsStream(name + ".class")) {
            if (input == null) { throw new IOException("Missing class: " + name); }
            ClassNode node = new ClassNode();
            new ClassReader(input).accept(node, ClassReader.SKIP_CODE | ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
            return node;
        }
    }

    private static Object value(AnnotationNode annotation, String key) {
        if (annotation.values != null) {
            for (int i = 0; i < annotation.values.size(); i += 2) {
                if (key.equals(annotation.values.get(i))) { return annotation.values.get(i + 1); }
            }
        }
        throw new IllegalArgumentException("Missing annotation member " + key);
    }

    private static List<AnnotationNode> annotations(List<AnnotationNode> visible, List<AnnotationNode> invisible) {
        List<AnnotationNode> result = new ArrayList<>();
        if (visible != null) { result.addAll(visible); }
        if (invisible != null) { result.addAll(invisible); }
        return result;
    }

    public static void main(String[] args) throws IOException {
        var config = JsonParser.parseString(Files.readString(Path.of("src/main/resources/passablefoliage.mixins.json"))).getAsJsonObject();
        String prefix = config.get("package").getAsString().replace('.', '/') + '/';
        int checked = 0;
        for (String group : List.of("mixins", "client")) {
            for (var entry : config.getAsJsonArray(group)) {
                ClassNode mixin = read(prefix + entry.getAsString().replace('.', '/'));
                ClassNode target = null;
                for (AnnotationNode annotation : annotations(mixin.visibleAnnotations, mixin.invisibleAnnotations)) {
                    if (annotation.desc.equals("Lorg/spongepowered/asm/mixin/Mixin;")) {
                        Object first = ((List<?>) value(annotation, "value")).getFirst();
                        target = read(((Type) first).getInternalName());
                    }
                }
                if (target == null) { throw new AssertionError("No target for " + mixin.name); }
                for (MethodNode handler : mixin.methods) {
                    for (AnnotationNode injection : annotations(handler.visibleAnnotations, handler.invisibleAnnotations)) {
                        boolean inject = injection.desc.equals("Lorg/spongepowered/asm/mixin/injection/Inject;");
                        boolean wrap = injection.desc.equals("Lcom/llamalad7/mixinextras/injector/wrapmethod/WrapMethod;");
                        if (!inject && !wrap) { continue; }
                        Type[] arguments = Type.getArgumentTypes(handler.desc);
                        Type[] captured = Arrays.copyOf(arguments, arguments.length - 1);
                        for (Object selectorObject : (List<?>) value(injection, "method")) {
                            String selector = (String) selectorObject;
                            int descriptorStart = selector.indexOf('(');
                            String methodName = descriptorStart < 0 ? selector : selector.substring(0, descriptorStart);
                            String descriptor = descriptorStart < 0 ? null : selector.substring(descriptorStart);
                            boolean matched = false;
                            for (MethodNode method : target.methods) {
                                if (!method.name.equals(methodName) || descriptor != null && !descriptor.equals(method.desc)) { continue; }
                                if (Arrays.equals(captured, Type.getArgumentTypes(method.desc)) &&
                                        (!wrap || Type.getReturnType(handler.desc).equals(Type.getReturnType(method.desc)))) {
                                    matched = true;
                                    break;
                                }
                            }
                            if (!matched) {
                                throw new AssertionError(mixin.name + '#' + handler.name + handler.desc + " does not match " + target.name + '#' + selector);
                            }
                            checked++;
                        }
                    }
                }
            }
        }
        if (checked < 10) { throw new AssertionError("Unexpectedly few injections: " + checked); }
        System.out.println("Mixin signatures: " + checked + " checked. Runtime transformations still require game testing.");
    }
}
