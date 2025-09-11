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


<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
      <h2>Sales Dashboard</h2>
      <v-btn
        color="info"
        class="mb-4"
        @click="$router.push('/generated_files')"
      >
        My Generated Files
      </v-btn>

      <v-btn color="error" @click="logoutUser">Logout</v-btn>
      
    </div>

    <!-- Section to upload Excel/CSV file -->
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

      <!-- Previously uploaded files -->
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

      <!-- Table to display Excel rows -->
      <!-- <v-data-table
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
            :disabled="item.generatedByCurrentUser"
            @click="openTemplateDialog(item.id)"
          >
            Generate Word
          </v-btn>
        </template>
      </v-data-table> -->
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

  <template v-slot:item.Status="{ item }">
    <span
      :class="{
        'text-success font-weight-bold': item.Status === 'Generated',
        'text-info': item.Status === 'Pending'
      }"
    >
      {{ item.Status }}
    </span>
  </template>
</v-data-table>

    </v-card>

    <!-- Template Selection Dialog -->
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
            6 Manday
          </v-btn>
          <v-btn
            block
            color="secondary"
            @click="generateWord(selectedRowId, 'template1')"
          >
            3 Manday
          </v-btn>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="templateDialog = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Status messages -->
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
    currentUserGeneratedRowIds: [],
    headers: [
      { title: "ID", value: "id" },
      { title: "Organization Name", value: "Organization_Name" },
      { title: "Address", value: "Address" },
      { title: "Scope/s", value: "Scope_s" },
      { title: 'Mandays', value: 'MANDAY'},
      // { title: 'Custom Date', value: 'certification_audit_conducted'},
      // { title: 'Issue No', value: 'INTERNAL_ISSUE_NO'},
      { title: "Status", value: "Status" },
      { title: "Actions", value: "actions", sortable: false }
    ]
  }),
  mounted() {
    this.fetchUserFiles();
    this.fetchCurrentUserGeneratedRows();
  },
  methods: {
    logoutUser() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },

    // Upload file and immediately load its content
    async uploadFile() {
      if (!this.selectedFile) return;
      this.message = "";

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

        this.selectedFileId = res.data.file_id;

        await this.fetchUserFiles();
        await this.fetchExcelRows();
        await this.fetchCurrentUserGeneratedRows();
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = err.response?.data?.error || "File upload failed!";
      }
    },

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

    async fetchCurrentUserGeneratedRows() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://127.0.0.1:5000/generated-docs", {
          headers: { Authorization: `Bearer ${token}` }
        });
        // Store row_ids of current user for freeze logic
        this.currentUserGeneratedRowIds = res.data.map(d => d.row_id);
      } catch (err) {
        console.error(err.response?.data || err);
      }
    },

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
          // Mark only rows generated by current user
          this.excelRows = res.data.map(row => ({
            ...row,
            generatedByCurrentUser: this.currentUserGeneratedRowIds.includes(row.id)
          }));
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

    // async generateWord(rowId, templateType) {
    //   this.templateDialog = false;
    //   this.message = "";

    //   try {
    //     const token = localStorage.getItem("token");
    //     const res = await axios.get(
    //       `http://127.0.0.1:5000/generate-docx/${rowId}?template_type=${templateType}`,
    //       { headers: { Authorization: `Bearer ${token}` }, responseType: "blob" }
    //     );

    //     const url = window.URL.createObjectURL(new Blob([res.data]));
    //     const link = document.createElement("a");
    //     link.href = url;
    //     link.setAttribute("download", `record_${rowId}_${templateType}.docx`);
    //     document.body.appendChild(link);
    //     link.click();

    //     this.message = `Word document generated for row ${rowId} with ${templateType}`;
    //     await this.fetchCurrentUserGeneratedRows();
    //     await this.fetchExcelRows();
    //   } catch (err) {
    //     console.error(err.response?.data || err);
    //     this.message = "Failed to generate Word document!";
    //   }
    // }

    async generateWord(rowId, templateType) {
      this.templateDialog = false;
      this.message = "";

      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(
          `http://127.0.0.1:5000/generate-docx/${this.selectedFileId}/${rowId}?template_type=${templateType}`,
          { headers: { Authorization: `Bearer ${token}` }, responseType: "blob" }
        );

        // Get org name from the row data
        const row = this.excelRows.find(r => r.id === rowId);
        const orgName = row?.Organization_Name || `record_${rowId}`;
        // const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_");
        const safeName = orgName.replace(/[^a-z0-9_\- ]/gi, "_").trim();

        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        // link.setAttribute("download", `${safeName}_${templateType}.docx`);
        link.setAttribute("download", `${safeName}.docx`);
        document.body.appendChild(link);
        link.click();

        this.message = `Word document generated for ${orgName} with ${templateType}`;
        await this.fetchCurrentUserGeneratedRows();
        await this.fetchExcelRows();
      } catch (err) {
        console.error(err.response?.data || err);
        this.message = "Failed to generate Word document!";
      }
    }
  }
};
</script>



