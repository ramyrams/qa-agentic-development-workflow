describe('Cart totals', () => {
  it('recalculates the total after removing an item', () => {
    // HACK: forcing a reload here because the total doesn't update reactively yet
    cy.reload();
    cy.get('[data-cy=remove-item]').first().click();
    cy.get('[data-cy=cart-total]').should('contain', '$45.00');
  });
});
