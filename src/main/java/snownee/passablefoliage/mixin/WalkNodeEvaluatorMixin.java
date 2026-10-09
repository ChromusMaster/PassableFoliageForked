package snownee.passablefoliage.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.level.pathfinder.WalkNodeEvaluator;
import snownee.passablefoliage.duck.PassableFoliageBlock;
import snownee.passablefoliage.PassableFoliageCommonConfig;

@Mixin(WalkNodeEvaluator.class)
public class WalkNodeEvaluatorMixin {
	@Inject(
			method = "getPathTypeFromState",
			at = @At("HEAD"),
			cancellable = true)
	private static void pfoliage_useCorrectPathType(
			BlockGetter level, BlockPos pos, CallbackInfoReturnable<PathType> cir) {
		if (!PassableFoliageCommonConfig.modifyPathFinding || PassableFoliageCommonConfig.playerOnly) {
			return;
		}
		BlockState state = level.getBlockState(pos);
		Block block = state.getBlock();
		if (block instanceof PassableFoliageBlock passableFoliageBlock && passableFoliageBlock.pfoliage$isPassable() &&
				state.getFluidState().isEmpty()) {
			cir.setReturnValue(PathType.OPEN);
		}
	}
}
