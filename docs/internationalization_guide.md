# Internationalization Guide

This guide describes how FLL-Sim supports multiple languages and localization.

## Features
- Language selection via GUI or config
- Translation management for UI elements
- Localization of documentation and help

## How to Enable
- Set preferred language in the GUI settings or config file
- Developers can add new translations using the `InternationalizationManager` in `src/fll_sim/education/internationalization.py`

## Developer Notes
- Use translation keys for all user-facing text
- Store translations in the `translations` dictionary
- Test UI in multiple languages

## Roadmap
- [ ] Add more language packs
- [ ] Automate translation updates
- [ ] Localize all documentation
