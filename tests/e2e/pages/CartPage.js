// tests/e2e/pages/CartPage.js
// Author: Salma Hani | ID: 120210255

class CartPage {
  constructor(page) {
    this.page = page;
    this.cartSidebar = page.locator('#cart-sidebar');
    this.checkoutBtn = page.locator('#proceed-to-checkout');
    this.cartItems = page.locator('.cart-item');
    this.totalDisplay = page.locator('#cart-total');
    this.errorMsg = page.locator('#cart-error');
  }

  async openCart() {
    await this.page.locator('#cart-toggle').click();
    await this.cartSidebar.waitFor({ state: 'visible' });
  }

  async proceedToCheckout() {
    await this.openCart();
    await this.checkoutBtn.click();
    await this.page.locator('#checkout-section').waitFor({ state: 'visible' });
  }

  async getTotal() {
    const text = await this.totalDisplay.textContent();
    return parseFloat(text.replace(/[^0-9.]/g, ''));
  }

  async getCartItemCount() {
    return await this.cartItems.count();
  }
}

module.exports = { CartPage };
