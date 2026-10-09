package snownee.passablefoliage.neoforge;

import com.mojang.serialization.MapCodec;
import net.neoforged.neoforge.common.conditions.ICondition;
import snownee.passablefoliage.PassableFoliageCommonConfig;

public record AlwaysLeafWalkingCondition() implements ICondition {
    public static final MapCodec<AlwaysLeafWalkingCondition> CODEC = MapCodec.unit(new AlwaysLeafWalkingCondition());

    @Override
    public boolean test(IContext context) {
        return PassableFoliageCommonConfig.alwaysLeafWalking;
    }

    @Override
    public MapCodec<? extends ICondition> codec() {
        return CODEC;
    }
}
