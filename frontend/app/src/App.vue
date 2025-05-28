<script setup>
import { RouterView, useRouter, useRoute } from "vue-router";
import { ref, watch, onMounted, onUnmounted, computed } from "vue";
import NavbarComponent from "./components/Navbar/NavbarComponent.vue";
import NavbarBottomMobileComponent from "./components/Navbar/NavbarBottomMobileComponent.vue";
import FooterComponent from "./components/FooterComponent.vue";
import {
    Notivue,
    Notification,
    NotivueSwipe,
    NotificationProgress,
    pastelTheme,
} from "notivue";
import { mobileNavItems } from "@/config/navigation.js";

const router = useRouter();
const route = useRoute();

const swipeableRouteNames = mobileNavItems.map(item => item.routeName);
const currentRouteIndex = ref(-1);
const windowWidth = ref(window.innerWidth);

const SWIPE_THRESHOLD = 75; // pixels
const MOBILE_BREAKPOINT = 992; // Corresponds to Bootstrap's lg breakpoint

const isMobile = computed(() => windowWidth.value < MOBILE_BREAKPOINT);

const updateCurrentRouteIndex = () => {
    const currentIndex = swipeableRouteNames.indexOf(route.name);
    currentRouteIndex.value = currentIndex;
};

watch(() => route.name, updateCurrentRouteIndex, { immediate: true });

const handleResize = () => {
    windowWidth.value = window.innerWidth;
};

onMounted(() => {
    window.addEventListener("resize", handleResize);
    updateCurrentRouteIndex(); // Initial check
});

onUnmounted(() => {
    window.removeEventListener("resize", handleResize);
});

const canSwipe = () => {
    // Add any other conditions if needed, e.g., check if a modal is open
    return isMobile.value;
};

const handleSwipeLeft = () => {
    if (!canSwipe() || currentRouteIndex.value === -1 || swipeableRouteNames.length === 0) {
        return; // Guard against invalid states
    }
    let nextIndex = currentRouteIndex.value + 1;
    if (nextIndex >= swipeableRouteNames.length) {
        nextIndex = 0; // Wrap around to the first item
    }
    const nextRouteName = swipeableRouteNames[nextIndex];
    router.push({ name: nextRouteName });
};

const handleSwipeRight = () => {
    if (!canSwipe() || currentRouteIndex.value === -1 || swipeableRouteNames.length === 0) {
        return; // Guard against invalid states
    }
    let prevIndex = currentRouteIndex.value - 1;
    if (prevIndex < 0) {
        prevIndex = swipeableRouteNames.length - 1; // Wrap around to the last item
    }
    const prevRouteName = swipeableRouteNames[prevIndex];
    router.push({ name: prevRouteName });
};

// Configuration for v-touch directive
const touchOptions = {
    swipeTolerance: SWIPE_THRESHOLD, // Use our defined threshold
    touchHoldTolerance: 500,
    disableClick: false, // Allow clicks on the content
};

</script>

<template>
    <Notivue v-slot="item">
        <NotivueSwipe :item="item">
            <Notification :item="item" :theme="pastelTheme">
                <NotificationProgress :item="item" />
            </Notification>
        </NotivueSwipe>
    </Notivue>
    <div class="d-flex flex-column min-vh-100">
        <!-- Top Navbar with safe-area padding -->
        <div class="bg-body-tertiary shadow-sm safe-area-top">
            <NavbarComponent class="container safe-area-container" />
        </div>

        <!-- Main content -->
        <main 
            class="container safe-area-container py-4 flex-grow-1"
            v-touch:swipe.left="handleSwipeLeft"
            v-touch:swipe.right="handleSwipeRight"
            v-touch-options="touchOptions"
        >
            <RouterView />
        </main>

        <!-- Desktop Footer -->
        <FooterComponent class="d-none d-lg-block shadow-sm" />

		<!-- Bottom Mobile Navbar with safe-area padding -->
		<NavbarBottomMobileComponent 
			class="d-lg-none d-block sticky-bottom shadow-sm safe-area-bottom"
		/>
	</div>
</template>

<style>
/* Top navbar safe area */
.safe-area-top {
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top);
}

/* Bottom mobile navbar safe area */
.safe-area-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
  background-clip: padding-box;
}

/* Main container safe areas */
.safe-area-container {
  padding-left: max(0.75rem, constant(safe-area-inset-left));
  padding-left: max(0.75rem, env(safe-area-inset-left));
  padding-right: max(0.75rem, constant(safe-area-inset-right));
  padding-right: max(0.75rem, env(safe-area-inset-right));
}
</style>
