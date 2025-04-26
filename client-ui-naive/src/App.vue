<template>
  <n-config-provider :theme="darkTheme">
    <n-message-provider>
      <!-- Header -->
      <n-layout-header class="header">
        <div class="title">SelfTrading</div>

        <!-- logout button — shown only when authenticated -->
        <n-button
          v-if="isAuth"
          class="logout-btn"
          quaternary
          circle
          size="large"
          @click="handleLogout"
        >
          <n-icon :size="22" :component="LogOutOutline" />
        </n-button>
      </n-layout-header>

      <!-- routed page -->
      <RouterView />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { darkTheme } from "naive-ui";
import { LogOutOutline } from "@vicons/ionicons5";
import { logout as doLogout } from "@/services/auth";

const router  = useRouter();
const isAuth  = ref(!!localStorage.getItem("token"));

function updateAuth() {
  isAuth.value = !!localStorage.getItem("token");
}

function handleLogout() {
  doLogout();                 // clears token + dispatches “auth-logout”
  updateAuth();
  router.push({ name: "Login" });
}

/* react to login / logout events */
onMounted(() => {
  window.addEventListener("auth-login", updateAuth);
  window.addEventListener("auth-logout", updateAuth);
});
onBeforeUnmount(() => {
  window.removeEventListener("auth-login", updateAuth);
  window.removeEventListener("auth-logout", updateAuth);
});
</script>

<style>
html, body, #app { height:100%; margin:0; background:#121212; }

/* fill full width, keep content left|right */
.header {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:16px;
  border-bottom:1px solid #444;
  background:#1a1a1a;
  color:#fff;
}
.title      { font-size:20px; font-weight:600; }
.logout-btn { margin-left:auto; }  /* forces button to right edge */
</style>
