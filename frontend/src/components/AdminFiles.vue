<template>
  <v-container>
    <!-- Top Bar -->
    <div class="d-flex justify-space-between align-center mb-6">
      <h2>All User Files</h2>
      <v-btn color="error" @click="logoutAdmin">Logout</v-btn>
    </div>

    <!-- User Filter -->
    <v-autocomplete
        v-model="selectedUser"
        :items="userOptions"
        item-title="username"
        item-value="id"
        label="Filter by User"
        clearable
        @update:modelValue="fetchFiles"
    />


    <!-- Files Table -->
    <v-data-table
      :headers="headers"
      :items="files"
      :items-per-page="10"
      class="elevation-6 rounded-xl"
    >
      <template v-slot:item.uploaded_at="{ item }">
        {{ new Date(item.uploaded_at).toLocaleString() }}
      </template>

      <template v-slot:item.actions="{ item }">
        <v-btn small color="primary" @click="downloadFile(item)">
          <v-icon small>mdi-download</v-icon> Download
        </v-btn>
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      files: [],
      headers: [
        { title: "File Name", value: "file_name" },
        { title: "Category", value: "category" },
        { title: "User", value: "user" },
        { title: "Source", value: "source" },
        { title: "Uploaded At", value: "uploaded_at" },
        { title: "Actions", value: "actions", sortable: false },
      ],
      userOptions: [],
      selectedUser: null,
    };
  },
  methods: {
    async fetchFiles() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("https://kvqa-data-application.onrender.com/admin/files", {
          headers: { Authorization: `Bearer ${token}` },
          params: this.selectedUser ? { user_id: this.selectedUser } : {},
        });
        this.files = res.data.files;
      } catch (err) {
        console.error(err);
      }
    },
    async fetchUsers() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("https://kvqa-data-application.onrender.com/users", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.userOptions = res.data.filter(u => u.role === "user");
      } catch (err) {
        console.error(err);
      }
    },
    async downloadFile(file) {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(`https://kvqa-data-application.onrender.com/download/${file.source}/${file.id}`, {
          headers: { Authorization: `Bearer ${token}` },
          responseType: "blob",
        });

        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", file.file_name);
        document.body.appendChild(link);
        link.click();
      } catch (err) {
        console.error("Download failed:", err);
      }
    },
    logoutAdmin() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },
  },
  mounted() {
    this.fetchFiles();
    this.fetchUsers();
  },
};
</script>
