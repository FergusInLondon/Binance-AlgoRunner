Feature: Account State
  The Account object manages state associated with an exchange user.
  The Account must be able to handle updates taken from user data, as well as
  coordinate with the Calculator and API Adapter to make transactions.

  Background:
    Given an account with no initial state
      and that account is currently awaiting messages

  Scenario: Stay synchronised with account updates
    Given an account update with full capabilities
     When that account update is processed
     Then the account should have full capabilities
    Given an account update with minimal capabilities
     When that account update is processed
     Then the account should have minimal capabilities

  Scenario: Stay synchronised with balance updates
    Given a BTC balance of 50 free and 25 locked
      And a balance update of 20 BTC
     When that balance update is processed
     Then the account should have a balance of 70 BTC free
    Given a balance update of -30 BTC 
     When that balance update is processed
     Then the account should have a balance of 40 BTC free

  Scenario: Stay synchronised with position updates
    Given an account position of BTC at 10 free and 25 locked
      and a position update of ETH at 20 free and 50 locked
     When that position update is processed 
     Then there should be a BTC balance of 10 free and 25 locked
      and there should be a ETH balance of 20 free and 50 locked
      and there should be a total of 2 balances
    Given a position update of BTC at 5 free and 30 locked
     When that position update is processed
     Then there should be a BTC balance of 5 free and 30 locked
      and there should be a ETH balance of 20 free and 50 locked
      and there should be a total of 2 balances

  Scenario: Process orders requests approved by the calculator
    Given a market order to buy BTC
      and the calculator will accept the order with a size of 0.0032
     When the order event is processed
     Then the API should recieve an order of 0.0032 BTC

  Scenario: Skip order requests rejected by the calculator
    Given a market order to buy BTC
      and the calculator will reject the order
     When the order event is processed
     Then the API should not recieve any orders
