<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
      <h2>My Generated Files</h2>
      <v-btn color="error" @click="$router.push('/dashboard')">Back to Dashboard</v-btn>
    </div>

    <v-alert v-if="message" type="info" dense border="left">
      {{ message }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="generatedDocs"
      item-key="id"
      dense
      class="elevation-1"
    >
      <template v-slot:item.download="{ item }">
        <v-btn small color="primary" @click="downloadFile(item.file_name)">
          Download
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
      generatedDocs: [],
      message: "",
      headers: [
        { title: "File Name", value: "file_name" },
        { title: "Generated At", value: "created_at" },
        { title: "Download", value: "download", sortable: false }
      ]
    };
  },
  mounted() {
    this.fetchGeneratedDocs();
  },
  methods: {
    async fetchGeneratedDocs() {
      this.message = "";
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://127.0.0.1:5000/generated-docs", {
        // const res = await axios.get("https://kvqa-data-application.onrender.com/generated-docs", {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.generatedDocs = res.data;  // Backend already filters by user_id
        if (!this.generatedDocs.length) {
          this.message = "You haven't generated any files yet.";
        }
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = "Failed to fetch generated files!";
      }
    },
    async downloadFile(fileName) {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `http://127.0.0.1:5000/download-generated-file/${fileName}`,
          // `https://kvqa-data-application.onrender.com/download-generated-file/${fileName}`,
          { headers: { Authorization: `Bearer ${token}` }, responseType: "blob" }
        );

        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", fileName);
        document.body.appendChild(link);
        link.click();
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = "Failed to download file!";
      }
    }
  }
};
</script>
