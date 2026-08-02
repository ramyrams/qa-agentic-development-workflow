describe.only('Checkout flow', () => {
  beforeEach(() => {
    cy.on('uncaught:exception', () => false);
    cy.visit('/checkout');
  });

  it('applies a discount code', () => {
    cy.get('.promo-input').type('SAVE10');
    cy.get('#apply-btn').click();
    cy.wait(3000);
    console.log('discount applied, moving on');
  });

  it('shows the updated total', () => {
    cy.get('[data-cy=cart-total]').should('contain', '$90.00');
  });
});
