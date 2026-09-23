---
title: Message Ordering in Distributed System
description: How to build a eventual consisen 
pubDate: 2026-09-22
tags: [backend]
draft: false
---

## Introduction 
**Searching** is the process of finding relevant information from a large collection of data based on what a user is looking for. At its core, a search system takes a user’s input—a keyword, phrase, or set of criteria—and returns the items that best match their intent, often ranked by how relevant each result is. This is a frequent recurring problem, for example
 - enterprise search, where users search relevant information from heterogeneous data sources (design doc, Slack, source code, team Wiki).
 - flight booking, where users search the most suitable flight given some hard constraints (landing date) and soft constraints (ticket price).
 - online shopping, where users search by some keyword, and need an ordered list depending on their own needs (latest-update, price from low to high).  

In this article, I will share a generic way to build a search system that is extensible and flexible, and show how this design paid off over the long arc of development