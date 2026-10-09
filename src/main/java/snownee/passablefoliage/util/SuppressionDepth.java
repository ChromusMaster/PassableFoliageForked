package snownee.passablefoliage.util;

/** A bounded, reusable counter per calling thread; never retains game objects. */
public final class SuppressionDepth {
    private final ThreadLocal<int[]> depth = ThreadLocal.withInitial(() -> new int[1]);

    public boolean isSuppressed() {
        return depth.get()[0] != 0;
    }

    public void enter() {
        int[] value = depth.get();
        if (value[0] == Integer.MAX_VALUE) {
            throw new IllegalStateException("Foliage suppression depth overflow");
        }
        value[0]++;
    }

    public void exit() {
        int[] value = depth.get();
        if (value[0] == 0) {
            throw new IllegalStateException("Unbalanced foliage suppression scope");
        }
        value[0]--;
    }
}
