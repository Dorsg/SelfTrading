<template>
  <n-config-provider :theme="darkTheme">
    <n-message-provider>
      <!-- ─────────── Header ─────────── -->
      <n-layout-header class="header">
        <div class="title">SelfTrading</div>

        <div v-if="isAuth" class="user-box">
          <n-tag
            round
            size="small"
            :bordered="false"
            :type="ibConnected ? 'success' : 'error'"
            class="ib-label"
          >
            <template #icon>
              <n-icon :component="ibConnected ? CheckmarkCircleOutline : CloseCircleOutline" />
            </template>
            IB
          </n-tag>

          <span class="uname">{{ capitalizedUsername }}</span>
          <n-tooltip trigger="hover" placement="bottom">
            <template #trigger>
              <n-button circle quaternary size="large" @click="handleLogout">
                <n-icon :size="27" :component="LogOutOutline" />
              </n-button>
            </template>
            Logout
          </n-tooltip>
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
  computed,
  watch,
  onMounted,
  onBeforeUnmount,
} from "vue";
import { useRouter } from "vue-router";
import { darkTheme } from "naive-ui";
import { LogOutOutline, CheckmarkCircleOutline, CloseCircleOutline } from "@vicons/ionicons5";
import {
  logout as doLogout,
  useCurrentUser,
} from "@/services/auth";
import { fetchIbStatus } from '@/services/dataManager';

const router = useRouter();
const ibConnected = ref(false);
let statusTimer = null;
const user   = useCurrentUser(); // reactive singleton
const isAuth = ref(!!user.value);

watch(user, (v) => (isAuth.value = !!v));

/* Capitalized username */
const capitalizedUsername = computed(() => {
  if (!user.value?.username) return "";
  return user.value.username.charAt(0).toUpperCase() + user.value.username.slice(1);
});

/* ───────── helpers ───────── */
function updateAuth() {
  isAuth.value = !!localStorage.getItem("token");
}

function handleLogout() {
  doLogout();
  updateAuth();
  router.push({ name: "Login" });
}

async function refreshIbStatus () {
  ibConnected.value = await fetchIbStatus();
}

/* listen for login / logout broadcasts */
onMounted(() => {
  refreshIbStatus();                 // first hit
  statusTimer = setInterval(refreshIbStatus, 10_000)
  window.addEventListener("auth-login",  updateAuth);
  window.addEventListener("auth-logout", updateAuth);
});
onBeforeUnmount(() => {
  clearInterval(statusTimer);
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
.title {
  font-size:20px;
  font-weight:600;
}
.user-box {
  display:flex;
  align-items:center;
  gap:14px;
}
.uname {
  font-size:16px;  /* bigger font */
  font-weight:600;
}
.ib-label {
  font-weight: 600;
}
</style>
