# Privacy Statement

Matcha is an open-source MLOps tool created and maintained by a global team of passionate engineers at Fuzzy Labs. We, alongside the broader Matcha community, seek to continuously enhance Matcha, and analytics are an important piece in shaping our efforts.

## Why we collect analytics

Our goal is to build a tool that is as useful, and as usable, as possible. In order to achieve this, it’s important that we’re able to understand how Matcha is used in the hands of our community.

Analytics and community engagement are vital in shaping the evolution of Matcha. As a small development team, we actively seek partnerships to grow or community and to support and extend our work in providing tooling that delights its users.

Not only do analytics allow us to build a user-informed roadmap for future features, but they also enable up to attract partnerships and community engagement that will support and accelerate this development.

None of the data we collect will be personally identifiable.

## How we collect analytics

Transparently. It’s important that everything we do, and everything we collect, is done so with the informed consent of our users. If ever something seems unclear, please get in touch. We’d love to chat.

What analytics we collect

We collect a variety of data from a number of different sources:

- pip download data
- direct developer to user conversations
- *anonymized* analytics from within the `matcha` tool


## `matcha` tool analytics

Within the tool we currently collect:

For each command that is run (e.g. `matcha provision`)
1. The command that was run
2. The timestamp of when the command was run
3. An anonymous random user ID, this is used to correctly identify the current number of users of our tool
4. An anonymous random state ID associated with your current `matcha.state` file
5. The type of operating system used e.g. `linux` or `darwin`

## Opting out

You can **opt-out** of in-tool usage analytics by running the CLI tool command:

```bash
matcha analytics opt-out
```
