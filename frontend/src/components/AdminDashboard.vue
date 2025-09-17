<template>
  <v-container>
    <!-- Top Bar -->
    <div class="d-flex justify-space-between align-center mb-6">
      <h2>Admin Dashboard</h2>
      <v-btn color="error" @click="logoutAdmin">Logout</v-btn>
    </div>

    <!-- Action Cards -->
    <v-row>
      <!-- Create User -->
      <v-col cols="12" md="6">
        <v-card class="pa-6" elevation="6" rounded="xl">
          <v-card-title>
            <v-icon color="primary" class="mr-2">mdi-account-plus</v-icon>
            Create User
          </v-card-title>
          <v-card-text>
            Add new users to the system with specific roles.
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="$router.push('/register')">Go to Create User</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- Access User Files -->
      <v-col cols="12" md="6">
        <v-card class="pa-6" elevation="6" rounded="xl">
          <v-card-title>
            <v-icon color="secondary" class="mr-2">mdi-file-document-multiple</v-icon>
            Manage User Files
          </v-card-title>
          <v-card-text>
            View and manage uploaded files for all users.
          </v-card-text>
          <v-card-actions>
            <v-btn color="secondary" @click="$router.push('/admin_files')">Go to Files</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  methods: {
    logoutAdmin() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.v-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.v-card:hover {
  transform: translateY(-4px);
  box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.15);
}
</style>
