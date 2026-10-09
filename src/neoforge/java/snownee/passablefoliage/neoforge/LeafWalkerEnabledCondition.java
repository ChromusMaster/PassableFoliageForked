package snownee.passablefoliage.neoforge;

import com.mojang.serialization.MapCodec;
import net.neoforged.neoforge.common.conditions.ICondition;
import snownee.passablefoliage.PassableFoliageCommonConfig;

public record LeafWalkerEnabledCondition() implements ICondition {
    public static final MapCodec<LeafWalkerEnabledCondition> CODEC = MapCodec.unit(new LeafWalkerEnabledCondition());

    @Override
    public boolean test(IContext context) {
        return PassableFoliageCommonConfig.leafWalkerEnabled;
    }

    @Override
    public MapCodec<? extends ICondition> codec() {
        return CODEC;
    }
}
