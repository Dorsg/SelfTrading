<template>
  <n-config-provider :theme="darkTheme">
    <n-message-provider>
      <!-- ─────────── Header ─────────── -->
      <n-layout-header class="header">
        <div class="title">SelfTrading</div>

        <div v-if="isAuth" class="user-box">
          <span class="uname">{{ user?.username }}</span>
          <n-button circle quaternary size="large" @click="handleLogout">
            <n-icon :size="22" :component="LogOutOutline" />
          </n-button>
        </div>
      </n-layout-header>

      <!-- ─────────── Routed view ─────────── -->
      <RouterView />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import {
  ref,
  watch,
  onMounted,
  onBeforeUnmount,
} from "vue";
import { useRouter } from "vue-router";
import { darkTheme } from "naive-ui";
import { LogOutOutline } from "@vicons/ionicons5";
import {
  logout as doLogout,
  useCurrentUser,          //  <<<─── added
} from "@/services/auth";

const router = useRouter();

const user   = useCurrentUser();        // reactive singleton
const isAuth = ref(!!user.value);

watch(user, (v) => (isAuth.value = !!v));

/* ───────── helpers ───────── */
function updateAuth() {
  isAuth.value = !!localStorage.getItem("token");
}

function handleLogout() {
  doLogout();
  updateAuth();
  router.push({ name: "Login" });
}

/* listen for login / logout broadcasts */
onMounted(() => {
  window.addEventListener("auth-login",  updateAuth);
  window.addEventListener("auth-logout", updateAuth);
});
onBeforeUnmount(() => {
  window.removeEventListener("auth-login",  updateAuth);
  window.removeEventListener("auth-logout", updateAuth);
});
</script>

<style>
html, body, #app { height:100%; margin:0; background:#121212; }

/* header */
.header {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:16px;
  border-bottom:1px solid #444;
  background:#1a1a1a;
  color:#fff;
}
.title   { font-size:20px; font-weight:600; }
.user-box{ display:flex; align-items:center; gap:12px; }
.uname   { font-weight:500; }
</style>
