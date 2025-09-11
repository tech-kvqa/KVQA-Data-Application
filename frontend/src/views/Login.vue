<template>
  <v-container class="d-flex justify-center align-center fill-height">
    <v-card class="pa-10" max-width="700" elevation="10" rounded="xl">
      <div class="text-center mb-8">
        <h2 class="font-weight-bold text-primary text-h4">KVQA KAF Login</h2>
        <p class="text-subtitle-1 grey--text">Sales User Portal</p>
      </div>

      <v-form>
        <v-text-field
          v-model="username"
          label="Username"
          outlined
          dense
          prepend-inner-icon="mdi-account"
          required
        ></v-text-field>

        <v-text-field
          v-model="password"
          label="Password"
          type="password"
          outlined
          dense
          prepend-inner-icon="mdi-lock"
          required
        ></v-text-field>

        <v-btn
          color="primary"
          class="mt-6"
          block
          x-large
          @click="loginUser"
        >
          Login
        </v-btn>

        <v-divider class="my-8"></v-divider>

        <div class="text-center">
          <span class="grey--text">Don’t have an account?</span>
          <v-btn
            text
            color="secondary"
            class="ml-2"
            @click="$router.push('/register')"
          >
            Register
          </v-btn>
        </div>
      </v-form>

      <p v-if="error" class="red--text text-center mt-4">{{ error }}</p>
    </v-card>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  data: () => ({
    username: "",
    password: "",
    error: ""
  }),
  methods: {
    async loginUser() {
      this.error = "";
      try {
        const res = await axios.post("http://127.0.0.1:5000/login", {
          username: this.username,
          password: this.password
        });
        localStorage.setItem("token", res.data.access_token);
        this.$router.push("/dashboard");
      } catch (err) {
        this.error = "Invalid username or password";
      }
    }
  }
};
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
  background: linear-gradient(135deg, #e3f2fd, #ffffff);
}
</style>
