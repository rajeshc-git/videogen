document.addEventListener("DOMContentLoaded", () => {
  // --------------------------------------------------------------------------
  // Theme Management (Light by Default, System Inherent, Dark Mode Support)
  // --------------------------------------------------------------------------
  const themeBtns = document.querySelectorAll(".theme-btn");
  const metaThemeColor = document.getElementById("metaThemeColor");

  // Default to 'light' as specifically requested by user ("by dfeutl no dakr mdoe lgiht mdoe")
  const savedTheme = localStorage.getItem("videogen_theme") || "light";
  applyTheme(savedTheme);

  themeBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const val = btn.getAttribute("data-theme-val");
      applyTheme(val);
      localStorage.setItem("videogen_theme", val);
    });
  });

  // Listen to OS theme changes if user chooses 'system'
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    if (localStorage.getItem("videogen_theme") === "system") {
      updateMetaThemeColor(e.matches ? "dark" : "light");
    }
  });

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    themeBtns.forEach((b) => {
      b.classList.toggle("active", b.getAttribute("data-theme-val") === theme);
    });

    let effectiveTheme = theme;
    if (theme === "system") {
      effectiveTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    updateMetaThemeColor(effectiveTheme);
  }

  function updateMetaThemeColor(effTheme) {
    if (metaThemeColor) {
      metaThemeColor.setAttribute("content", effTheme === "dark" ? "#07080e" : "#f8fafc");
    }
  }

  // --------------------------------------------------------------------------
  // Mobile Tab Navigation (for Smartphone Viewports)
  // --------------------------------------------------------------------------
  const mobileViewTabs = document.getElementById("mobileViewTabs");
  const tabBtnCreate = document.getElementById("tabBtnCreate");
  const tabBtnPreview = document.getElementById("tabBtnPreview");
  const videoReadyDot = document.getElementById("videoReadyDot");

  function setMobileTab(tabName) {
    document.body.setAttribute("data-mobile-tab", tabName);
    tabBtnCreate.classList.toggle("active", tabName === "create");
    tabBtnPreview.classList.toggle("active", tabName === "preview");
  }

  tabBtnCreate.addEventListener("click", () => setMobileTab("create"));
  tabBtnPreview.addEventListener("click", () => setMobileTab("preview"));
  setMobileTab("create");

  // --------------------------------------------------------------------------
  // DOM Elements
  // --------------------------------------------------------------------------
  const dropzone = document.getElementById("dropzone");
  const imageInput = document.getElementById("imageInput");
  const dropzonePlaceholder = document.getElementById("dropzonePlaceholder");
  const previewContainer = document.getElementById("previewContainer");
  const imagePreview = document.getElementById("imagePreview");
  const btnChangeImage = document.getElementById("btnChangeImage");

  const promptInput = document.getElementById("promptInput");
  const btnSurprisePrompt = document.getElementById("btnSurprisePrompt");
  const durationSelect = document.getElementById("durationSelect");
  const btnGenerate = document.getElementById("btnGenerate");

  const comfyStatusBadge = document.getElementById("comfyStatusBadge");
  const comfyStatusText = document.getElementById("comfyStatusText");
  const gpuText = document.getElementById("gpuText");

  const playerEmptyState = document.getElementById("playerEmptyState");
  const playerProgressOverlay = document.getElementById("playerProgressOverlay");
  const progressBarFill = document.getElementById("progressBarFill");
  const progressStatusTitle = document.getElementById("progressStatusTitle");
  const progressPercentageText = document.getElementById("progressPercentageText");
  const progressStepDetail = document.getElementById("progressStepDetail");
  const videoPlayer = document.getElementById("videoPlayer");
  const downloadActionBar = document.getElementById("downloadActionBar");
  const downloadButton = document.getElementById("downloadButton");
  const generationStateText = document.getElementById("generationStateText");

  const modelsGrid = document.getElementById("modelsGrid");
  const modelsCountBadge = document.getElementById("modelsCountBadge");
  const btnCollapse = document.getElementById("btnCollapse");
  const activeDownloadBanner = document.getElementById("activeDownloadBanner");
  const activeDownloadTitle = document.getElementById("activeDownloadTitle");
  const activeDownloadSpeed = document.getElementById("activeDownloadSpeed");
  const downloadProgressBar = document.getElementById("downloadProgressBar");
  const activeDownloadBytes = document.getElementById("activeDownloadBytes");
  const activeDownloadPercent = document.getElementById("activeDownloadPercent");
  const btnCancelDl = document.getElementById("btnCancelDl");

  let selectedImageFile = null;
  let currentJobId = null;
  let jobPollInterval = null;
  let allModelsReady = false;

  // --------------------------------------------------------------------------
  // Prompts & Audio Vibe Chips
  // --------------------------------------------------------------------------
  const SAMPLE_PROMPTS = [
    "Editorial tech product film. The subject floats weightlessly with warm orange and electric cyan rim lighting. A slow deliberate push-in reveals glowing internal details. Audio: deep pulsing sub-bass room tone, sharp tactile mechanical clicks, and a rising electronic swell resolving smoothly.",
    "Cinematic vertical portrait in golden hour light. Gentle breeze caresses hair, soft sunlight sweeping across the scene with warm anamorphic flare. Audio: gentle ocean breeze, soft orchestral violin swell, serene nature atmosphere.",
    "Cyberpunk neon alleyway sequence. Raindrops falling in slow motion with vibrant purple and cyan reflections on the wet asphalt, camera rotating smoothly around the subject. Audio: driving synthesizer pulse, crisp rain textures, distant thunder, and a futuristic riser.",
    "Sci-fi spaceship command bridge. Holographic telemetry displays flickering with neon cyan particles as the commander turns slowly toward the camera. Audio: deep warp drive hum, high-tech computer blips, smooth pneumatic whoosh on motion."
  ];

  const AUDIO_VIBE_SNIPPETS = {
    cinematic: " Audio: dramatic orchestral strings swell, low sub-bass impact, atmospheric room tone.",
    cyberpunk: " Audio: driving retro synthesizer arpeggio, punchy electronic beat, futuristic riser.",
    nature: " Audio: soothing ocean waves, gentle wind breeze, soft atmospheric birdsong.",
    lofi: " Audio: warm electric piano chords, relaxing lo-fi vinyl warmth, soft bassline.",
    action: " Audio: heavy cinematic trailer braam, aggressive rising percussion, high tension riser."
  };

  promptInput.value = SAMPLE_PROMPTS[0];

  btnSurprisePrompt.addEventListener("click", () => {
    const randomIdx = Math.floor(Math.random() * SAMPLE_PROMPTS.length);
    promptInput.value = SAMPLE_PROMPTS[randomIdx];
  });

  document.querySelectorAll(".audio-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const vibe = chip.getAttribute("data-vibe");
      const snippet = AUDIO_VIBE_SNIPPETS[vibe];
      if (snippet) {
        // Strip any existing "Audio: ..." and append the new one
        const parts = promptInput.value.split("Audio:");
        promptInput.value = parts[0].trim() + snippet;
      }
    });
  });

  // --------------------------------------------------------------------------
  // Image Selection & 9:16 Preview
  // --------------------------------------------------------------------------
  dropzone.addEventListener("click", (e) => {
    if (e.target !== btnChangeImage) {
      imageInput.click();
    }
  });

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleSelectedImage(e.dataTransfer.files[0]);
    }
  });

  imageInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleSelectedImage(e.target.files[0]);
    }
  });

  btnChangeImage.addEventListener("click", (e) => {
    e.stopPropagation();
    imageInput.click();
  });

  function handleSelectedImage(file) {
    if (!file.type.startsWith("image/")) {
      alert("Please upload a valid image file (PNG, JPG, WEBP).");
      return;
    }
    selectedImageFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      dropzonePlaceholder.classList.add("hidden");
      previewContainer.classList.remove("hidden");
      btnGenerate.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  // --------------------------------------------------------------------------
  // System Status & Offline Models Checking
  // --------------------------------------------------------------------------
  async function checkSystemStatus() {
    try {
      const res = await fetch("/api/status");
      if (!res.ok) return;
      const data = await res.json();

      // ComfyUI Status
      if (data.comfy && data.comfy.online) {
        comfyStatusBadge.className = "status-chip status-chip-online";
        comfyStatusText.textContent = `ComfyUI Online (v${data.comfy.version || "0.42"})`;
        if (data.comfy.device) {
          gpuText.textContent = data.comfy.device.replace(" : cudaMallocAsync", "");
        }
      } else {
        comfyStatusBadge.className = "status-chip status-chip-connecting";
        comfyStatusText.textContent = "ComfyUI Connecting...";
      }

      // Models
      if (data.models) {
        allModelsReady = data.models.all_ready;
        renderModelsList(data.models.models);
      }

      // Active Download
      if (data.download && data.download.is_downloading) {
        activeDownloadBanner.classList.remove("hidden");
        activeDownloadTitle.textContent = `Downloading ${data.download.model_name}...`;
        activeDownloadSpeed.textContent = `${data.download.speed_mb} MB/s`;
        downloadProgressBar.style.width = `${data.download.percent}%`;
        const dlGB = (data.download.downloaded_bytes / (1024 ** 3)).toFixed(2);
        const totGB = (data.download.total_bytes / (1024 ** 3)).toFixed(2);
        activeDownloadBytes.textContent = `${dlGB} GB / ${totGB} GB`;
        activeDownloadPercent.textContent = `${data.download.percent}%`;
      } else {
        activeDownloadBanner.classList.add("hidden");
      }
    } catch (err) {
      console.error("Status check failed:", err);
    }
  }

  function renderModelsList(models) {
    let readyCount = 0;
    modelsGrid.innerHTML = "";

    models.forEach((m) => {
      if (m.exists) readyCount++;
      const card = document.createElement("div");
      card.className = "model-card-item";
      card.innerHTML = `
        <div class="model-card-top">
          <span class="model-card-name">${m.name}</span>
          <span class="model-tag ${m.exists ? "model-tag-ready" : ""}">${m.exists ? "Ready" : "Missing"}</span>
        </div>
        <p class="model-card-desc">${m.desc}</p>
        <div class="model-card-bot">
          <span class="model-card-size">${m.exists ? m.size_gb + " GB" : "Expected: ~" + m.expected_gb + " GB"}</span>
          ${
            m.exists
              ? `<button class="btn-get-model is-installed" disabled>✓ Installed</button>`
              : `<button class="btn-get-model" onclick="triggerModelDownload('${m.name}')">Download</button>`
          }
        </div>
      `;
      modelsGrid.appendChild(card);
    });

    modelsCountBadge.textContent = `${readyCount} / ${models.length} Ready`;
    modelsCountBadge.classList.toggle("badge-ready", readyCount === models.length);
  }

  window.triggerModelDownload = async (modelName) => {
    const formData = new FormData();
    formData.append("model_name", modelName);
    const res = await fetch("/api/models/download", {
      method: "POST",
      body: formData,
    });
    const d = await res.json();
    if (!d.success) {
      alert(d.message);
    }
    checkSystemStatus();
  };

  btnCancelDl.addEventListener("click", async () => {
    await fetch("/api/models/cancel", { method: "POST" });
    checkSystemStatus();
  });

  // Drawer Toggle
  btnCollapse.addEventListener("click", () => {
    const isHidden = modelsGrid.classList.contains("hidden");
    modelsGrid.classList.toggle("hidden", !isHidden);
    btnCollapse.querySelector("span:first-child").textContent = isHidden ? "Close" : "Details";
    btnCollapse.querySelector(".arrow-indicator").textContent = isHidden ? "▴" : "▾";
  });

  // --------------------------------------------------------------------------
  // Generation Pipeline & Execution
  // --------------------------------------------------------------------------
  btnGenerate.addEventListener("click", async (e) => {
    e.preventDefault();
    if (!selectedImageFile) {
      alert("Please upload an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedImageFile);
    formData.append("prompt", promptInput.value.trim());
    formData.append("duration", durationSelect.value);
    formData.append("mode", allModelsReady ? "auto" : "demo");

    // UI Updates
    btnGenerate.disabled = true;
    playerEmptyState.classList.add("hidden");
    videoPlayer.classList.add("hidden");
    downloadActionBar.classList.add("hidden");
    playerProgressOverlay.classList.remove("hidden");
    videoReadyDot.classList.add("hidden");

    progressBarFill.style.width = "5%";
    progressPercentageText.textContent = "5%";
    progressStepDetail.textContent = "Formatting 9:16 canvas & submitting job...";
    generationStateText.textContent = "Generating...";

    // On mobile, auto-switch to Preview Player tab so user watches the live progress!
    if (window.innerWidth <= 768) {
      setMobileTab("preview");
    }

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      currentJobId = data.job_id;

      if (jobPollInterval) clearInterval(jobPollInterval);
      jobPollInterval = setInterval(pollJobProgress, 500);
    } catch (err) {
      alert("Error starting generation: " + err.message);
      btnGenerate.disabled = false;
      playerProgressOverlay.classList.add("hidden");
      playerEmptyState.classList.remove("hidden");
    }
  });

  async function pollJobProgress() {
    if (!currentJobId) return;
    try {
      const res = await fetch(`/api/progress/${currentJobId}`);
      if (!res.ok) return;
      const job = await res.json();

      progressBarFill.style.width = `${job.progress}%`;
      progressPercentageText.textContent = `${job.progress}%`;
      progressStepDetail.textContent = job.step || "Processing...";

      if (job.status === "completed") {
        clearInterval(jobPollInterval);
        playerProgressOverlay.classList.add("hidden");
        videoPlayer.classList.remove("hidden");
        videoPlayer.src = job.video_url;
        videoPlayer.play();

        downloadActionBar.classList.remove("hidden");
        downloadButton.href = job.video_url;
        downloadButton.setAttribute("download", job.filename || "MiniMaxH3_916.mp4");

        videoReadyDot.classList.remove("hidden");
        btnGenerate.disabled = false;
        generationStateText.textContent = "Ready ✨";
      } else if (job.status === "failed") {
        clearInterval(jobPollInterval);
        playerProgressOverlay.classList.add("hidden");
        playerEmptyState.classList.remove("hidden");
        alert("Generation failed: " + (job.error || "Unknown error"));
        btnGenerate.disabled = false;
        generationStateText.textContent = "Failed";
      }
    } catch (err) {
      console.error("Progress poll error:", err);
    }
  }

  // Check system status once on startup (stops permanently once ComfyUI is verified online)
  checkSystemStatus();
});
