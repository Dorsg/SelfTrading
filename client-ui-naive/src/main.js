// client-ui-naive/src/main.js
import { createApp } from "vue";
import App from "./App.vue";
import { createNaiveUI } from "./naive";

import router from "@/router";          
import { setAuthHeader } from "@/services/auth";

const saved = localStorage.getItem("token");
if (saved) setAuthHeader(saved);

const app = createApp(App);
app.use(createNaiveUI());
app.use(router);                        
app.mount("#app");