// tests/e2e/pages/TrackingPage.js
// Author: Salma Hani | ID: 120210255

class TrackingPage {
  constructor(page) {
    this.page = page;
    this.statusSteps = page.locator('.status-step');
    this.activeStep  = page.locator('.status-step.active');
    this.orderIdDisplay = page.locator('#order-id-display');
  }

  async gotoOrder(orderId) {
    await this.page.goto(`http://localhost:5000/track/${orderId}`);
  }

  async getActiveStepName() {
    return await this.activeStep.textContent();
  }

  async getAllStepNames() {
    return await this.statusSteps.allTextContents();
  }

  async waitForStatusChange(expectedStatus, timeout = 5000) {
    await this.page.waitForFunction(
      (status) => document.querySelector('.status-step.active')?.textContent?.includes(status),
      expectedStatus,
      { timeout }
    );
  }
}

module.exports = { TrackingPage };
