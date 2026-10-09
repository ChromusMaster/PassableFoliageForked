package snownee.passablefoliage.util;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;

public final class PlatformSound {
    private PlatformSound() { }

    public static SoundType getSoundType(BlockState state, Level level, BlockPos pos, Entity entity) {
        return ((net.neoforged.neoforge.common.extensions.IBlockStateExtension) state).getSoundType(level, pos, entity);
    }
}
