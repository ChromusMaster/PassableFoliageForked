package snownee.passablefoliage;


import org.jspecify.annotations.Nullable;

import com.mojang.serialization.MapCodec;

import net.fabricmc.fabric.api.resource.conditions.v1.ResourceCondition;
import net.fabricmc.fabric.api.resource.conditions.v1.ResourceConditionType;
import net.minecraft.resources.RegistryOps;

public final class AlwaysLeafWalkingCondition implements ResourceCondition {
	public static final AlwaysLeafWalkingCondition INSTANCE = new AlwaysLeafWalkingCondition();
	public static final ResourceConditionType<AlwaysLeafWalkingCondition> TYPE = ResourceConditionType.create(
			PassableFoliage.id("always_leaf_walking"), MapCodec.unit(INSTANCE));

	private AlwaysLeafWalkingCondition() {
	}

	@Override
	public ResourceConditionType<?> getType() {
		return TYPE;
	}

	@Override
	public boolean test(RegistryOps.@Nullable RegistryInfoLookup registryInfo) {
		return PassableFoliageCommonConfig.alwaysLeafWalking;
	}
}
