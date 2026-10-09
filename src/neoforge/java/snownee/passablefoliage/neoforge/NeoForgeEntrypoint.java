package snownee.passablefoliage.neoforge;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.conditions.ICondition;
import net.neoforged.neoforge.event.TagsUpdatedEvent;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;
import snownee.passablefoliage.EnchantmentModule;
import snownee.passablefoliage.PassableFoliage;
import snownee.passablefoliage.PassableFoliageCommonConfig;

@Mod(PassableFoliage.ID)
public final class NeoForgeEntrypoint {
    public NeoForgeEntrypoint(IEventBus modBus) {
        PassableFoliageCommonConfig.load(FMLPaths.CONFIGDIR.get());
        DeferredRegister<DataComponentType<?>> effects = DeferredRegister.create(
                Registries.ENCHANTMENT_EFFECT_COMPONENT_TYPE, PassableFoliage.ID);
        effects.register("leaf_walker", () -> EnchantmentModule.LEAF_WALKER);
        effects.register(modBus);
        DeferredRegister<MapCodec<? extends ICondition>> conditions = DeferredRegister.create(
                NeoForgeRegistries.Keys.CONDITION_CODECS, PassableFoliage.ID);
        conditions.register("leaf_walker_enabled", () -> LeafWalkerEnabledCondition.CODEC);
        conditions.register("always_leaf_walking", () -> AlwaysLeafWalkingCondition.CODEC);
        conditions.register(modBus);
        NeoForge.EVENT_BUS.addListener(NeoForgeEntrypoint::tagsUpdated);
    }

    private static void tagsUpdated(TagsUpdatedEvent event) {
        if (event.shouldUpdateStaticData()) {
            PassableFoliage.tagsLoaded();
        }
    }
}
