describe('User profile page', () => {
  it('displays the user avatar', () => {
    // TODO: replace with data-cy selector once the avatar component is refactored
    cy.get('[data-cy=avatar]').should('be.visible');
  });

  it('allows editing the display name', () => {
    cy.get('[data-cy=edit-name]').click();
    cy.get('[data-cy=name-input]').clear().type('New Name');
    cy.get('[data-cy=save-btn]').click();
    // FIXME: this assertion is too weak, check the actual saved value via API
    cy.get('[data-cy=name-display]').should('be.visible');
  });
});
