describe('Checkout flow', () => {
  beforeEach(() => {
    cy.visit('/checkout');
  });

  it('applies a discount code and updates the total', () => {
    cy.intercept('POST', '/api/cart/promo').as('applyPromo');
    cy.get('[data-cy=promo-input]').type('SAVE10');
    cy.get('[data-cy=apply-btn]').click();
    cy.wait('@applyPromo');
    cy.get('[data-cy=cart-total]').should('contain', '$90.00');
  });

  it('shows an error for an invalid discount code', () => {
    cy.intercept('POST', '/api/cart/promo').as('applyPromo');
    cy.get('[data-cy=promo-input]').type('INVALID');
    cy.get('[data-cy=apply-btn]').click();
    cy.wait('@applyPromo');
    cy.get('[data-cy=promo-error]').should('be.visible');
  });
});
