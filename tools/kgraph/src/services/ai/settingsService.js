class AISettingsService {
  constructor() {
    this.loadSettings();
  }

  loadSettings() {
    const savedSettings = localStorage.getItem('modelSettings');
    if (savedSettings) {
      const { model, temperature } = JSON.parse(savedSettings);
      this.model = model;
      this.temperature = temperature;
    } else {
      this.model = 'openai/gpt-4-turbo';
      this.temperature = 0.7;
    }
  }

  updateSettings() {
    const savedSettings = localStorage.getItem('modelSettings');
    if (savedSettings) {
      const { model, temperature } = JSON.parse(savedSettings);
      this.model = model;
      this.temperature = temperature;
      console.log('AISettingsService: Settings updated:', { model, temperature });
    }
  }

  getModel() {
    return this.model;
  }

  getTemperature() {
    return this.temperature;
  }
}

export const aiSettingsService = new AISettingsService();
