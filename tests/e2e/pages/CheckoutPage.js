// tests/e2e/pages/CheckoutPage.js
// Author: Salma Hani | ID: 120210255

class CheckoutPage {
  constructor(page) {
    this.page = page;
    this.cardInput    = page.locator('#card-number');
    this.expiryInput  = page.locator('#card-expiry');
    this.cvvInput     = page.locator('#card-cvv');
    this.submitBtn    = page.locator('#confirm-payment');
    this.successMsg   = page.locator('#order-confirmation');
    this.errorMsg     = page.locator('#payment-error');
  }

  async fillCard(number, expiry, cvv) {
    await this.cardInput.fill(number);
    await this.expiryInput.fill(expiry);
    await this.cvvInput.fill(cvv);
  }

  async submit() {
    await this.submitBtn.click();
  }

  async waitForConfirmation(timeout = 8000) {
    await this.successMsg.waitFor({ timeout });
    return await this.successMsg.textContent();
  }

  async waitForError(timeout = 8000) {
    await this.errorMsg.waitFor({ timeout });
    return await this.errorMsg.textContent();
  }
}

module.exports = { CheckoutPage };
