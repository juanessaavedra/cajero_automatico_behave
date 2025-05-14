# ATM Gherkin Features (Spanish messages)

Feature: Temu Bank ATM Machine
  As a bank customer
  I want to use the ATM machine
  So that I can manage my bank account securely and efficiently

  Scenario: Successful authentication
    Given I am on the ATM login screen
    When I enter the password "12345"
    And I click the "Login" button
    Then I should see the main menu
    And I should see my available balance of "$700,000.00"

  Scenario: Check account balance
    Given I have successfully logged in
    And I am on the main menu
    When I select the "Check Balance" option
    Then I should see the balance inquiry screen
    And I should see the message "Su saldo actual es:"
    And I should have the option to "Volver al Menú"

  Scenario: Successful money withdrawal
    Given I have successfully logged in
    And my current balance is "$700,000.00"
    When I select the "Withdraw Money" option
    And I enter the amount "100000"
    And I click the "Withdraw" button
    Then I should see the message "Retiro exitoso. Ha retirado: $100,000.00"
    And my balance should be updated to "$600,000.00"
    And I should return to the main menu

  Scenario: Money deposit
    Given I have successfully logged in
    And my current balance is "$600,000.00"
    When I select the "Deposit Money" option
    And I enter the amount "50000"
    And I click the "Deposit" button
    Then I should see the message "Depósito exitoso. Ha depositado: $50,000.00"
    And my balance should be updated to "$650,000.00"
    And I should return to the main menu

  Scenario: Successful password change
    Given I have successfully logged in
    And I am on the main menu
    When I select the "Change Password" option
    And I enter my current password "12345"
    And I enter my new password "67890"
    And I confirm my new password "67890"
    And I click the "Change" button
    Then I should see the message "¡Contraseña cambiada exitosamente!"
    And I should return to the main menu
    And I should be able to log out
    And log in with the new password "67890"

  Scenario: Withdrawal attempt with insufficient funds
    Given I have successfully logged in
    And my current balance is "$100,000.00"
    When I select the "Withdraw Money" option
    And I enter the amount "200000"
    And I click the "Withdraw" button
    Then I should see the message "Fondos insuficientes para realizar el retiro"
    And my balance should remain at "$100,000.00"
    And I should stay on the withdrawal screen