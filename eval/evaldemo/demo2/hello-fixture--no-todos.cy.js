describe('User profile page', () => {
  it('displays the user avatar', () => {
    cy.get('[data-cy=avatar]').should('be.visible');
  });

  it('allows editing the display name', () => {
    cy.intercept('PUT', '/api/profile').as('saveProfile');
    cy.get('[data-cy=edit-name]').click();
    cy.get('[data-cy=name-input]').clear().type('New Name');
    cy.get('[data-cy=save-btn]').click();
    cy.wait('@saveProfile');
    cy.get('[data-cy=name-display]').should('contain', 'New Name');
  });
});
