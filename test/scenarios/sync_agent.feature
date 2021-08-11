Feature: Sync Agent
  The Sync Agent runs as an Actor, embedded within the Strategy.
  The agent is responsible for maintaining a snapshot of the current state
  of an account - meaning all orders and balances - whilst also coordinating
  any market orders that are required.

  Scenario: Stay synchronised with account updates
    Given a running sync agent awaiting messages
      and an account update with full capabilities
     When all messages are processed
     Then the account should have full capabilities
    Given an account update with minimal capabilities
     When all messages are processed
     Then the account should have minimal capabilities
     When the sync agent is stopped
     Then it should no longer be running

  Scenario: Stay synchronised with balance updates
    Given a running sync agent awaiting messages
      and a BTC balance of 50 free and 25 locked
      And a balance update of 20 BTC
     When all messages are processed
     Then the account should have a balance of 70 BTC free
    Given a balance update of -30 BTC 
     When all messages are processed
     Then the account should have a balance of 40 BTC free
     When the sync agent is stopped
     Then it should no longer be running

  Scenario: Stay synchronised with position updates
    Given a running sync agent awaiting messages
      and an account position of BTC at 10 free and 25 locked
      and a position update of ETH at 20 free and 50 locked
     When all messages are processed
     Then there should be a BTC balance of 10 free and 25 locked
      and there should be a ETH balance of 20 free and 50 locked
      and there should be a total of 2 balances
    Given a position update of BTC at 5 free and 30 locked
     When all messages are processed
     Then there should be a BTC balance of 5 free and 30 locked
      and there should be a ETH balance of 20 free and 50 locked
      and there should be a total of 2 balances
     When the sync agent is stopped
     Then it should no longer be running

  Scenario: Process authorised transaction requests
    Given a running sync agent awaiting messages
    Given a request to buy BTC
      and the order of BTC is accepted with a size of 0.0032
     When all messages are processed
     Then the API should recieve an order of 0.0032 BTC
     When the sync agent is stopped
     Then it should no longer be running

  Scenario: Skip declined transaction requests
    Given a running sync agent awaiting messages
      and a request to buy BTC
      and the order is declined
     When all messages are processed
     Then the API should not recieve any orders
     When the sync agent is stopped
     Then it should no longer be running
