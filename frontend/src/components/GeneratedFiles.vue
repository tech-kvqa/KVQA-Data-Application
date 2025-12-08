<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
      <h2>My Generated Files</h2>
      <div>
        <v-btn
          color="primary"
          class="mr-2"
          :outlined="viewMode !== 'docs'"
          @click="switchMode('docs')"
        >
          Documents
        </v-btn>
        <v-btn
          color="secondary"
          class="mr-2"
          :outlined="viewMode !== 'checklists'"
          @click="switchMode('checklists')"
        >
          Checklists
        </v-btn>
        <v-btn color="error" @click="$router.push('/dashboard')">Back to Dashboard</v-btn>
      </div>
    </div>

    <v-alert v-if="message" type="info" dense border="left">
      {{ message }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="viewMode === 'docs' ? generatedDocs : generatedChecklists"
      item-key="id"
      dense
      class="elevation-1"
    >
      <template v-slot:item.download="{ item }">
        <v-btn
          small
          color="primary"
          @click="downloadFile(item.file_name, viewMode)"
        >
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
      generatedChecklists: [],
      viewMode: "docs",
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
    switchMode(mode) {
      this.viewMode = mode;
      this.message = "";

      const category = this.$route.query.category;
      
      if (mode === "docs" && !this.generatedDocs.length) {
        this.fetchGeneratedDocs();
      } else if (mode === "checklists" && !this.generatedChecklists.length) {
        this.fetchGeneratedChecklists();
      }
    },

    async fetchGeneratedDocs() {
      try {
        const token = localStorage.getItem("token");
        const category = this.$route.query.category || null;
        const company = localStorage.getItem("company") || null;

        const url = category
          ? `https://kvqa-data-application.onrender.com/generated-docs?category=${category}&company=${company}`
          : `https://kvqa-data-application.onrender.com/generated-docs?company=${company}`;

        const res = await axios.get(url, {
          headers: { Authorization: `Bearer ${token}` },
        });

        this.generatedDocs = res.data;
        this.message = this.generatedDocs.length
          ? ""
          : `No generated documents found for ${category || "any category"}.`;
      } catch (error) {
        console.error(error);
        this.message = "Failed to fetch generated documents.";
      }
    },

    async fetchGeneratedChecklists() {
      try {
        const token = localStorage.getItem("token");
        const category = this.$route.query.category || null;
        const company = localStorage.getItem("company") || null;

        console.log("Fetching checklist category:", category);

        const url = category
          ? `https://kvqa-data-application.onrender.com/generated-checklists?category=${category}&company=${company}`
          : `https://kvqa-data-application.onrender.com/generated-checklists?company=${company}`;

        const res = await axios.get(url, {
          headers: { Authorization: `Bearer ${token}` },
        });

        this.generatedChecklists = res.data;

        this.message = this.generatedChecklists.length
          ? ""
          : `No checklist documents found for ${category || "any category"}.`;
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = "Failed to fetch generated checklists!";
      }
    },
    async downloadFile(fileName, mode) {
      try {
        const token = localStorage.getItem("token");
        const endpoint =
          mode === "docs"
            ? `https://kvqa-data-application.onrender.com/download-generated-file/${fileName}`
            : `https://kvqa-data-application.onrender.com/download-checklist-file/${fileName}`;

        const res = await axios.get(endpoint, {
          headers: { Authorization: `Bearer ${token}` },
          responseType: "blob"
        });

        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", fileName);
        document.body.appendChild(link);
        link.click();
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = `Failed to download ${mode === "docs" ? "document" : "checklist"}!`;
      }
    }
  }
};
</script>
