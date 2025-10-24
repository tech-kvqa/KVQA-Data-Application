<!-- <template>
  <v-container>
    <h2 class="mb-4">Sales Dashboard</h2>
    <v-btn color="error" @click="logoutUser">Logout</v-btn>

    <v-card class="pa-4 mt-4">
      <h3>Test Protected API</h3>
      <v-btn color="primary" class="mt-2" @click="getProtected">
        Call /protected
      </v-btn>
      <p class="mt-2">{{ message }}</p>
    </v-card>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  data: () => ({
    message: ""
  }),
  methods: {
    logoutUser() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },
    async getProtected() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://127.0.0.1:5000/protected", {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.message = res.data.message;
      } catch (err) {
        this.message = "Unauthorized or expired session!";
      }
    }
  }
};
</script> -->


<!-- <template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
      <h2>Sales Dashboard</h2>
      <v-btn color="error" @click="logoutUser">Logout</v-btn>
    </div> -->

    <!-- Section to load Excel data -->
    <!-- <v-card class="pa-6 mb-6" outlined>
      <h3 class="mb-4">Available Records</h3>
      <v-btn color="primary" class="mb-4" @click="fetchExcelRows">
        Load Excel Data
      </v-btn>

      <v-data-table
        :headers="headers"
        :items="excelRows"
        item-key="id"
        dense
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
            <v-btn
                small
                color="success"
                :disabled="item.Status === 'Generated'"
                @click="openTemplateDialog(item.id)"
            >
                Generate Word
            </v-btn>
        </template>
      </v-data-table>
    </v-card> -->

    <!-- Template Selection Dialog -->
    <!-- <v-dialog v-model="templateDialog" max-width="400">
      <v-card>
        <v-card-title>Select Template</v-card-title>
        <v-card-text>
          <v-btn block color="primary" class="mb-2" @click="generateWord(selectedRowId, 'template2')">
            2 Day 2 Auditor
          </v-btn>
          <v-btn block color="secondary" @click="generateWord(selectedRowId, 'template1')">
            2 Day 1 Auditor
          </v-btn>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="templateDialog = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog> -->

    <!-- Status messages -->
    <!-- <v-alert
      v-if="message"
      type="info"
      class="mt-4"
      dense
      border="left"
    >
      {{ message }}
    </v-alert>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  data: () => ({
    message: "",
    excelRows: [],
    templateDialog: false,
    selectedRowId: null,
    // selectedTemplate: null,
    headers: [
      { title: "ID", value: "id" },
      { title: "Organization Name", value: "Organization_Name" },
      { title: "Address", value: "Address" },
      { title: "Scope/s", value: "Scope_s" },
      { title: "Status", value: "Status" },
      { title: "Actions", value: "actions", sortable: false }
    ]
  }),
  methods: {
    logoutUser() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },

    async fetchExcelRows() {
      this.message = "";
      try {
        const token = localStorage.getItem("token")?.trim();
        console.log("Token being sent:", token);

        const res = await axios.get("http://127.0.0.1:5000/excel-rows", {
          headers: { Authorization: `Bearer ${token}` },
          withCredentials: true
        });

        if (Array.isArray(res.data)) {
          this.excelRows = res.data.map(row =>
            Object.fromEntries(
              Object.entries(row).map(([key, val]) => [key, val ?? ""])
            )
          );
        } else {
          console.error("Unexpected response format:", res.data);
          this.excelRows = [];
          this.message = res.data?.error || "Failed to fetch Excel data!";
        }
      } catch (err) {
        console.error("Fetch error:", err.response?.data || err);
        this.message = err.response?.data?.error || "Failed to fetch Excel data!";
      }
    },

    openTemplateDialog(rowId) {
      this.selectedRowId = rowId;
      // this.selectedTemplate = null;
      this.templateDialog = true;
    },

    closeDialog() {
      this.templateDialog = false;
      this.selectedTemplate = null;
    },

    async generateWord(rowId, templateType) {
      this.templateDialog = false;
      this.message = "";
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `http://127.0.0.1:5000/generate-docx/${rowId}?template_type=${templateType}`,
          {
            headers: { Authorization: `Bearer ${token}` },
            responseType: "blob"
          }
        );

        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `record_${rowId}_${templateType}.docx`);
        document.body.appendChild(link);
        link.click();

        this.message = `Word document generated for row ${rowId} with ${templateType}`;
        await this.fetchExcelRows();
      } catch (err) {
        console.error("Generate error:", err.response?.data || err);
        this.message = "Failed to generate Word document!";
      }
    }
  }
};
</script> -->


<!-- <template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
      <h2>Sales Dashboard</h2>
      <v-btn color="error" @click="logoutUser">Logout</v-btn>
    </div>

    <v-card class="pa-6 mb-6" outlined>
      <h3 class="mb-4">Upload Your File</h3>

      <v-file-input
        v-model="selectedFile"
        label="Select Excel/CSV file"
        accept=".xlsx,.xls,.csv"
        outlined
        dense
        class="mb-4"
      ></v-file-input>

      <v-btn
        color="primary"
        class="mb-4"
        :disabled="!selectedFile"
        @click="uploadFile"
      >
        Upload File
      </v-btn>

      <h3 class="mb-2">Your Uploaded Files</h3>
      <v-select
        v-model="selectedFileId"
        :items="userFiles"
        item-text="file_name"
        item-value="id"
        label="Select a file to view data"
        outlined
        dense
        class="mb-4"
        @change="fetchExcelRows"
      ></v-select>

      <v-data-table
        :headers="headers"
        :items="excelRows"
        item-key="id"
        dense
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <v-btn
            small
            color="success"
            :disabled="item.Status === 'Generated'"
            @click="openTemplateDialog(item.id)"
          >
            Generate Word
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="templateDialog" max-width="400">
      <v-card>
        <v-card-title>Select Template</v-card-title>
        <v-card-text>
          <v-btn
            block
            color="primary"
            class="mb-2"
            @click="generateWord(selectedRowId, 'template2')"
          >
            2 Day 2 Auditor
          </v-btn>
          <v-btn
            block
            color="secondary"
            @click="generateWord(selectedRowId, 'template1')"
          >
            2 Day 1 Auditor
          </v-btn>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="templateDialog = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-alert
      v-if="message"
      type="info"
      class="mt-4"
      dense
      border="left"
    >
      {{ message }}
    </v-alert>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  data: () => ({
    message: "",
    excelRows: [],
    templateDialog: false,
    selectedRowId: null,
    selectedFile: null,
    selectedFileId: null,
    userFiles: [],
    headers: [
      { title: "ID", value: "id" },
      { title: "Organization Name", value: "Organization_Name" },
      { title: "Address", value: "Address" },
      { title: "Scope/s", value: "Scope_s" },
      { title: "Status", value: "Status" },
      { title: "Actions", value: "actions", sortable: false }
    ]
  }),
  mounted() {
    this.fetchUserFiles();
  },
  methods: {
    logoutUser() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },

    // Upload file and immediately load its content
    async uploadFile() {
      this.message = "";
      if (!this.selectedFile) return;

      try {
        const token = localStorage.getItem("token");
        const formData = new FormData();
        formData.append("file", this.selectedFile);

        const res = await axios.post(
          "http://127.0.0.1:5000/upload-file",
          formData,
          {
            headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" }
          }
        );

        this.message = res.data.message;
        this.selectedFile = null;

        // Set the newly uploaded file as selected and load its data
        this.selectedFileId = res.data.file_id;
        await this.fetchExcelRows();

        // Refresh the list of user files
        await this.fetchUserFiles();
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = err.response?.data?.error || "File upload failed!";
      }
    },

    // Fetch all files uploaded by the user
    async fetchUserFiles() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://127.0.0.1:5000/my-files", {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.userFiles = res.data;
      } catch (err) {
        console.error(err.response?.data || err);
      }
    },

    // Fetch rows from selected Excel/CSV file
    async fetchExcelRows() {
      if (!this.selectedFileId) return;
      this.message = "";
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `http://127.0.0.1:5000/excel-rows/${this.selectedFileId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (Array.isArray(res.data)) {
          this.excelRows = res.data.map(row =>
            Object.fromEntries(
              Object.entries(row).map(([key, val]) => [key, val ?? ""])
            )
          );
        } else {
          this.excelRows = [];
          this.message = res.data?.error || "Failed to fetch data!";
        }
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = err.response?.data?.error || "Failed to fetch data!";
      }
    },

    openTemplateDialog(rowId) {
      this.selectedRowId = rowId;
      this.templateDialog = true;
    },

    async generateWord(rowId, templateType) {
      this.templateDialog = false;
      this.message = "";
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `http://127.0.0.1:5000/generate-docx/${rowId}?template_type=${templateType}`,
          { headers: { Authorization: `Bearer ${token}` }, responseType: "blob" }
        );

        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `record_${rowId}_${templateType}.docx`);
        document.body.appendChild(link);
        link.click();

        this.message = `Word document generated for row ${rowId} with ${templateType}`;
        await this.fetchExcelRows(); // refresh table status
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = "Failed to generate Word document!";
      }
    }
  }
};
</script> -->


<!-- <template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
      <h2>Category Dashboard</h2>
      <v-btn color="error" @click="logoutUser">Logout</v-btn>
    </div>

    <v-card class="pa-6">
      <h3 class="mb-4">Select a Category</h3>

      <v-btn block color="primary" class="mb-2" @click="$router.push('/qms_dashboard')">
        QMS Dashboard
      </v-btn>

      <v-btn block color="secondary" class="mb-2" @click="$router.push('/ems_dashboard')">
        EMS Dashboard
      </v-btn>

      <v-btn block color="success" @click="$router.push('/oshas_dashboard')">
        OHSAS Dashboard
      </v-btn>
    </v-card>

    <v-alert type="info" class="mt-6" dense border="left">
      👉 Select a category above to manage its Excel uploads, view rows,
      and generate Word documents with the respective templates.
    </v-alert>
  </v-container>
</template>

<script>
export default {
  methods: {
    logoutUser() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    }
  }
};
</script> -->

<template>
  <v-container>
    <!-- Header -->
    <div class="d-flex justify-space-between align-center mb-8">
      <h2 class="text-h5 font-weight-bold">📊 Category Dashboard</h2>
      <v-btn color="error" variant="flat" @click="logoutUser">
        <v-icon start>mdi-logout</v-icon> Logout
      </v-btn>
    </div>

    <!-- Category Cards -->
    <v-row dense>
      <!-- QMS -->
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

      <!-- EMS -->
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

      <!-- OHSAS -->
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

      <!-- IMS -->
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

    <!-- Info Alert -->
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
  methods: {
    logoutUser() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },
  },
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