<template>
  <n-config-provider :theme="darkTheme">
    <n-message-provider>
      <n-layout class="login-layout">
        <n-card
          class="login-card"
          :title="isLogin ? 'Login to SelfTrading' : 'Create an Account'"
          :style="{ width: isLogin ? '360px' : '720px' }"
        >
          <n-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-placement="top"
            label-width="auto"
            require-mark-placement="right-hanging"
          >
            <!-- Username -->
            <n-form-item label="Username" path="username">
              <n-input
                v-model:value="form.username"
                placeholder="Enter your username"
                :input-props="{ autocomplete: 'username' }"
              />
            </n-form-item>

            <!-- Password -->
            <n-form-item label="Password" path="password">
              <n-input
                type="password"
                show-password-on="click"
                v-model:value="form.password"
                placeholder="Enter your password"
                :input-props="{ autocomplete: 'current-password' }"
              />
            </n-form-item>

            <!-- Sign-Up Only Fields -->
            <template v-if="!isLogin">
              <n-grid :cols="2" :x-gap="16">
                <!-- Confirm Password -->
                <n-form-item-gi label="Confirm Password" path="confirmPassword">
                  <n-input
                    type="password"
                    show-password-on="click"
                    v-model:value="form.confirmPassword"
                    placeholder="Confirm your password"
                    :input-props="{ autocomplete: 'new-password' }"
                  />
                </n-form-item-gi>

                <n-form-item-gi label="Email" path="email">
                  <n-input
                    type="email"
                    v-model:value="form.email"
                    placeholder="Enter your email"
                    :input-props="{ autocomplete: 'email' }"
                  />
                </n-form-item-gi>

                <n-form-item-gi label="IB Username" path="ibUser">
                  <n-input
                    v-model:value="form.ibUser"
                    placeholder="Enter your IB username"
                    :input-props="{ autocomplete: 'off' }"
                  />
                </n-form-item-gi>

                <n-form-item-gi label="IB Password" path="ibPassword">
                  <n-input
                    type="password"
                    show-password-on="click"
                    v-model:value="form.ibPassword"
                    placeholder="Enter your IB password"
                    :input-props="{ autocomplete: 'new-password' }"
                  />
                </n-form-item-gi>
              </n-grid>
            </template>

            <!-- Submit Button -->
            <n-form-item>
              <n-button
                type="primary"
                block
                :loading="loading"
                @click="isLogin ? handleLogin() : handleSignup()"
              >
                {{ isLogin ? "Login" : "Sign Up" }}
              </n-button>
            </n-form-item>
          </n-form>

          <!-- Toggle Login / Sign-Up -->
          <div class="switch-auth-mode">
            <n-button text @click="isLogin = !isLogin">
              {{
                isLogin
                  ? "Don't have an account? Sign Up"
                  : "Already have an account? Login"
              }}
            </n-button>
          </div>
        </n-card>
      </n-layout>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { ref } from "vue";
import { darkTheme, useMessage } from "naive-ui";

const emit = defineEmits(["login-success"]);

const formRef = ref(null);
const message = useMessage();
const loading = ref(false);
const isLogin = ref(true);

const form = ref({
  username: "",
  password: "",
  confirmPassword: "",
  email: "",
  ibUser: "",
  ibPassword: "",
});

const rules = {
  username: {
    required: true,
    message: "Username is required",
    trigger: "blur",
  },
  password: {
    required: true,
    message: "Password is required",
    trigger: "blur",
  },
  // only runs when confirmPassword field is rendered
  confirmPassword: {
    required: true,
    message: "Please confirm your password",
    trigger: "blur",
    validator: (rule, value) => {
      if (!isLogin.value && value !== form.value.password) {
        return new Error("Passwords do not match");
      }
      return true;
    },
  },
  email: {
    required: true,
    message: "Email is required",
    trigger: "blur",
    validator: (rule, value) => {
      // simple email check
      return /^\S+@\S+\.\S+$/.test(value) ? true : new Error("Invalid email");
    },
  },
  ibUser: {
    required: true,
    message: "IB username is required",
    trigger: "blur",
  },
  ibPassword: {
    required: true,
    message: "IB password is required",
    trigger: "blur",
  },
};

// Mock server calls
function mockLogin(username, password) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (username === "admin" && password === "123") {
        resolve("OK");
      } else {
        reject(new Error("Invalid username or password"));
      }
    }, 1000);
  });
}

function mockSignup(data) {
  return new Promise((resolve) => {
    setTimeout(() => {
      // you could inspect `data` here
      resolve("Signed up");
    }, 1000);
  });
}

function handleLogin() {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      loading.value = true;
      try {
        await mockLogin(form.value.username, form.value.password);
        message.success("Login successful");
        emit("login-success");
      } catch (err) {
        message.error(err.message);
      } finally {
        loading.value = false;
      }
    } else {
      message.error("Please fix form errors");
    }
  });
}

function handleSignup() {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      loading.value = true;
      try {
        await mockSignup(form.value);
        message.success("Sign-up successful, you can now log in");
        isLogin.value = true;
        // reset IB fields & passwords
        form.value.confirmPassword = "";
        form.value.ibUser = "";
        form.value.ibPassword = "";
      } catch {
        message.error("Sign-up failed");
      } finally {
        loading.value = false;
      }
    } else {
      message.error("Please fix form errors");
    }
  });
}
</script>

<style scoped>
.login-layout {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 130px); /* matches header offset */
}

.login-card {
  padding: 24px;
  background-color: #1a1a1a;
  border: 1px solid #444;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
  color: white;
}

.switch-auth-mode {
  margin-top: 12px;
  text-align: center;
}
</style>
