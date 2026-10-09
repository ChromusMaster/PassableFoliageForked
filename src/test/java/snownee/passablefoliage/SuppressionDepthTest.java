package snownee.passablefoliage;

import java.util.concurrent.atomic.AtomicReference;
import snownee.passablefoliage.util.SuppressionDepth;

public final class SuppressionDepthTest {
    private SuppressionDepthTest() { }

    private static void check(boolean value, String message) {
        if (!value) { throw new AssertionError(message); }
    }

    public static void main(String[] args) throws InterruptedException {
        SuppressionDepth scope = new SuppressionDepth();
        check(!scope.isSuppressed(), "Initially suppressed");
        scope.enter();
        scope.enter();
        scope.exit();
        check(scope.isSuppressed(), "Nested exit cleared outer scope");
        AtomicReference<Throwable> failure = new AtomicReference<>();
        Thread worker = new Thread(() -> {
            try {
                check(!scope.isSuppressed(), "Suppression leaked across threads");
                scope.enter();
                scope.exit();
            } catch (Throwable error) {
                failure.set(error);
            }
        });
        worker.start();
        worker.join();
        if (failure.get() != null) { throw new AssertionError("Thread isolation", failure.get()); }
        check(scope.isSuppressed(), "Other thread modified outer scope");
        scope.exit();
        check(!scope.isSuppressed(), "Final exit did not reset");
        try {
            scope.enter();
            try { throw new IllegalArgumentException("test"); }
            finally { scope.exit(); }
        } catch (IllegalArgumentException expected) {
            check(!scope.isSuppressed(), "Exception leaked scope");
        }
        try {
            scope.exit();
            throw new AssertionError("Underflow was not rejected");
        } catch (IllegalStateException expected) {
            check(!scope.isSuppressed(), "Underflow corrupted scope");
        }
        for (int i = 0; i < 100_000; i++) { scope.enter(); scope.exit(); }
        check(!scope.isSuppressed(), "Repeated usage corrupted scope");
        System.out.println("SuppressionDepth: nested scopes, thread isolation, exceptions, underflow and reuse passed.");
    }
}
