<template>
    <nav class="navbar bg-body-tertiary text-center" v-if="authStore.isAuthenticated">
        <div class="container-fluid justify-content-around">
            <router-link
                v-for="item in navItems"
                :key="item.routeName"
                :to="{ name: item.routeName }"
                class="nav-link link-body-emphasis"
            >
                <font-awesome-icon :icon="item.icon" />
                <br />
                {{ $t(item.labelKey) }}
            </router-link>
        </div>
    </nav>
    <FooterComponent v-else />
</template>

<script>
import { useRouter } from "vue-router";
// Importing the i18n
import { useI18n } from 'vue-i18n'
// import the stores
import { useAuthStore } from '@/stores/authStore'
// Import the components
import FooterComponent from '@/components/FooterComponent.vue'
import UserAvatarComponent from '@/components/Users/UserAvatarComponent.vue'
// Import Notivue push
import { push } from "notivue";
// Import navigation items
import { mobileNavItems } from "@/config/navigation.js";

export default {
    components: {
        UserAvatarComponent,
        FooterComponent,
    },
    setup() {
        const router = useRouter();
        const authStore = useAuthStore();
        const { locale, t } = useI18n();

        async function handleLogout() {
            try {
                await authStore.logoutUser(router, locale);
            } catch (error) {
                push.error(`${t("navbarComponent.errorLogout")} - ${error}`);
            }
        }

        return {
            authStore,
            handleLogout,
            navItems: mobileNavItems, // Expose navItems to the template
        };
    },
};
</script>

