Tickets
=======

:total-count: 15

--------------------------------------------------------------------------------

Optimize requests
=================

:bugid: 1
:created: 2021-06-05T17:23:08
:priority: 0

- [x] use mset when possible
- [x] avoid requests when possible

- [x] review atomicity of keys/values:
    - nbPlayers can be removed (look at array length instead)

--------------------------------------------------------------------------------

Intermission during game
========================

:bugid: 2
:created: 2021-06-06T14:54:52
:priority: 0

-When a player is idle , give to other player a minigame or a question about the idle player
-Then show the result in a funny manner

--------------------------------------------------------------------------------

Who's turn is it ?
==================

:bugid: 4
:created: 2021-06-06T14:54:52
:priority: 0

-Start the game immediately

--------------------------------------------------------------------------------

Do something between turn of other player
=========================================

:bugid: 5
:created: 2021-06-06T14:54:52
:priority: 0

--------------------------------------------------------------------------------

Handle errors on dice throws (421 dice already thrown)
======================================================

:bugid: 7
:created: 2021-06-06T14:54:52
:priority: 0

New docs created to detail the errors

--------------------------------------------------------------------------------

Game dont detect losers
=======================

:bugid: 8
:created: 2021-06-06T14:54:52
:priority: 0

-Start the game immediately

--------------------------------------------------------------------------------

JWT support
===========

:bugid: 11
:created: 2021-06-09T14:52:59
:priority: 0

Upgrade the current cookie handling with proper JWT
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

--------------------------------------------------------------------------------

Add job queue support
=====================

:bugid: 12
:created: 2021-06-09T16:34:38
:priority: 0

https://arq-docs.helpmanual.io/
https://python-rq.org/

rabbitmq ?


Will be used for timeouts...

--------------------------------------------------------------------------------

Look for a way to get const variables in vue app
================================================

:bugid: 13
:created: 2021-06-09T21:10:24
:priority: 0

const values are not in reach of vue templating motor. To ease our coding we must find a way to access it easily

--------------------------------------------------------------------------------

Client should know dice throws
==============================

:bugid: 14
:created: 2021-06-10T17:59:40
:priority: 0

When a player reconnect , client doesnt know his last throws. Thus blocking the player for making his choice

--------------------------------------------------------------------------------

change PlayersData attr from "diceValue" to "remainingPoint"
============================================================

:bugid: 15
:created: 2021-06-10T18:00:51
:priority: 0
