<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-8">
      <h2 class="text-h5 font-weight-bold">📊 Category Dashboard</h2>
      <div class="mb-8" style="max-width: 250px;">
        <v-select
          v-model="selectedCompany"
          :items="['APL', 'CSPL']"
          label="Select Company"
          outlined
          density="compact"
        ></v-select>
      </div>

      <v-btn color="error" variant="flat" @click="logoutUser">
        <v-icon start>mdi-logout</v-icon> Logout
      </v-btn>
    </div>

    <v-row dense>
      <v-col cols="12" md="4">
        <v-card
          class="pa-6 d-flex flex-column align-center justify-center text-center rounded-xl cursor-pointer hover-card"
          elevation="4"
          @click="$router.push('/qms_dashboard')"
        >
          <v-icon size="48" color="primary" class="mb-4">mdi-clipboard-check-outline</v-icon>
          <h3 class="text-h6 font-weight-medium mb-2">QMS Dashboard</h3>
          <p class="text-body-2 text-medium-emphasis">
            Manage Quality Management uploads and reports.
          </p>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card
          class="pa-6 d-flex flex-column align-center justify-center text-center rounded-xl cursor-pointer hover-card"
          elevation="4"
          @click="$router.push('/ems_dashboard')"
        >
          <v-icon size="48" color="secondary" class="mb-4">mdi-leaf</v-icon>
          <h3 class="text-h6 font-weight-medium mb-2">EMS Dashboard</h3>
          <p class="text-body-2 text-medium-emphasis">
            Handle Environmental Management reports.
          </p>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card
          class="pa-6 d-flex flex-column align-center justify-center text-center rounded-xl cursor-pointer hover-card"
          elevation="4"
          @click="$router.push('/oshas_dashboard')"
        >
          <v-icon size="48" color="success" class="mb-4">mdi-shield-account</v-icon>
          <h3 class="text-h6 font-weight-medium mb-2">OHSAS Dashboard</h3>
          <p class="text-body-2 text-medium-emphasis">
            Access Occupational Health & Safety dashboard.
          </p>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card
          class="pa-6 d-flex flex-column align-center justify-center text-center rounded-xl cursor-pointer hover-card"
          elevation="4"
          @click="$router.push('/ims_dashboard')"
        >
          <v-icon size="48" color="success" class="mb-4">mdi-shield-account</v-icon>
          <h3 class="text-h6 font-weight-medium mb-2">IMS Dashboard</h3>
          <p class="text-body-2 text-medium-emphasis">
            Access Occupational Health,Safety dashboard, Environment and Quality Management.
          </p>
        </v-card>
      </v-col>
    </v-row>

    <v-alert
      type="info"
      class="mt-8"
      density="comfortable"
      border="start"
      variant="tonal"
    >
      <v-icon start>mdi-information-outline</v-icon>
      Select a category above to manage its Excel uploads, view rows,
      and generate Word documents with the respective templates.
    </v-alert>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      selectedCompany: localStorage.getItem("company") || "APL"
    };
  },
  methods: {
    logoutUser() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },
  },
  watch: {
    selectedCompany(newVal) {
      localStorage.setItem("company", newVal);
    }
  }
};
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
.hover-card:hover {
  transform: translateY(-4px);
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15) !important;
}
</style>