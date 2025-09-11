<template>
  <v-container class="d-flex justify-center align-center fill-height">
    <v-card class="pa-10" max-width="600" elevation="10" rounded="xl">
      <div class="text-center mb-6">
        <h2 class="font-weight-bold text-primary">Register New User</h2>
        <p class="text-subtitle-1 grey--text">Create your account</p>
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

        <v-text-field
          v-model="confirmPassword"
          label="Confirm Password"
          type="password"
          outlined
          dense
          prepend-inner-icon="mdi-lock-check"
          required
        ></v-text-field>

        <v-btn color="primary" class="mt-6" block x-large @click="registerUser">
          Register
        </v-btn>
      </v-form>

      <p v-if="error" class="red--text text-center mt-4">{{ error }}</p>
      <p v-if="success" class="green--text text-center mt-4">{{ success }}</p>

      <div class="text-center mt-6">
        <span class="grey--text">Already have an account?</span>
        <v-btn text color="secondary" class="ml-2" @click="$router.push('/login')">
          Back to Login
        </v-btn>
      </div>
    </v-card>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  data: () => ({
    username: "",
    password: "",
    confirmPassword: "",
    error: "",
    success: ""
  }),
  methods: {
    async registerUser() {
      this.error = "";
      this.success = "";

      if (this.password !== this.confirmPassword) {
        this.error = "Passwords do not match";
        return;
      }

      try {
        // await axios.post("http://127.0.0.1:5000/register", {
        await axios.post("https://kvqa-data-application.onrender.com/register", {
          username: this.username,
          password: this.password
        });
        this.success = "User registered successfully. You can now log in.";
        this.username = "";
        this.password = "";
        this.confirmPassword = "";
      } catch (err) {
        this.error = err.response?.data?.error || "Registration failed";
      }
    }
  }
};
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f9ff, #ffffff);
}
</style>
