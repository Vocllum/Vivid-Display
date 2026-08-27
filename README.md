# Vivid Display

Vivid Display is a Windows-only Stream Deck plugin for smooth software display dimming. It uses a non-interactive desktop overlay, so it does not change monitor hardware brightness, DDC/CI state, Gamma Ramp, ICC profiles, or display drivers.

## Features

- One unified **Brightness** action for keys, encoders, and Stream Deck + touch feedback.
- Adjust by step, set a preset brightness, or toggle dimming.
- Target all displays, the primary display, the display under the pointer, or a specific display.
- 5% minimum-brightness safeguard enabled by default; it can be disabled to allow 0%.
- HDR-aware display topology handling.
- English and Simplified Chinese localization.
- Self-contained Windows x64 native host bundled in the Marketplace package.

## Requirements

- Windows 10 22H2 or Windows 11
- Stream Deck 7.1 or later
- Node.js 24+ for development
- .NET 8 SDK or later for development

## Build and verify

Run these commands from Windows PowerShell:

```powershell
npm.cmd install
npm.cmd run typecheck
npm.cmd test
npm.cmd run build
node scripts/smoke-host.mjs
npm.cmd run validate
npx.cmd streamdeck pack com.vocllum.vivid-display.sdPlugin
```

The plugin package is generated under `release/1.0.0.0/` by the Windows build workflow. It is intentionally excluded from source control; Marketplace distributes the packaged artifact.

## Limitations

The overlay is designed for the normal Windows desktop. It may not appear on the secure desktop, login or lock screen, or in some exclusive full-screen applications. The overlay participates in ordinary screenshots and recordings.

## Marketplace

The Marketplace listing is the distribution source for the signed/DRM-processed plugin package. This repository contains the source, build instructions, tests, and documentation.

The listing URL will be added after Elgato assigns the product page.

## Support

Please open an issue with your Windows version, Stream Deck version, plugin version, and a concise reproduction. Do not include private screenshots or logs containing personal data.

## Privacy

The plugin does not collect analytics or send display data to a remote service. It uses a local named pipe between the Stream Deck plugin and its bundled Windows host.

## License

MIT. See [LICENSE](LICENSE).

## Attribution

Built with the official [Elgato Stream Deck SDK](https://docs.elgato.com/streamdeck/sdk/).

See [PROJECT_OUTLINE.md](PROJECT_OUTLINE.md) for the architecture and compatibility matrix.

## Documentation

- [Project outline](PROJECT_OUTLINE.md)
- [Release convention](docs/release-convention.md)
- [Elgato plugin guidelines](https://docs.elgato.com/guidelines/stream-deck/plugins/)
- [Elgato Marketplace product guidelines](https://docs.elgato.com/guidelines/products/)

Version 1.0.0.0 is prepared for Marketplace review.

