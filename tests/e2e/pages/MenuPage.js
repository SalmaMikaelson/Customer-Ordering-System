// tests/e2e/pages/MenuPage.js
// Author: Salma Hani | ID: 120210255

class MenuPage {
  constructor(page) {
    this.page = page;
    this.menuItems = page.locator('.menu-item');
    this.cartBadge = page.locator('#cart-badge');
    this.outOfStockBadge = page.locator('.out-of-stock-badge');
  }

  async goto() {
    await this.page.goto('http://localhost:5000');
  }

  async addItemToCart(itemName) {
    const item = this.page.locator('.menu-item', { hasText: itemName });
    await item.locator('.add-to-cart-btn').click();
  }

  async isItemDisabled(itemName) {
    const btn = this.page.locator('.menu-item', { hasText: itemName }).locator('.add-to-cart-btn');
    return await btn.isDisabled();
  }

  async getCartCount() {
    return parseInt(await this.cartBadge.textContent(), 10);
  }
}

module.exports = { MenuPage };
