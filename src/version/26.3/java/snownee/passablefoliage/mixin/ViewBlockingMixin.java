package snownee.passablefoliage.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.state.BlockBehaviour.BlockStateBase;
import net.minecraft.world.level.block.state.BlockState;
import snownee.passablefoliage.PassableFoliage;
import snownee.passablefoliage.PassableFoliageCommonConfig;
import net.minecraft.world.phys.AABB;

@Mixin(BlockStateBase.class)
public class ViewBlockingMixin {
	@Inject(at = @At("HEAD"), method = "isViewBlocking", cancellable = true)
	private void pfoliage_isViewBlocking(
			BlockGetter level,
			BlockPos pos,
			AABB bounds,
			CallbackInfoReturnable<Boolean> ci) {
		if (PassableFoliageCommonConfig.alwaysNotViewBlocking && PassableFoliage.isPassable((BlockState) (Object) this)) {
			ci.setReturnValue(false);
		}
	}

}
