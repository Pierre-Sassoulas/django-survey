# Agent instructions

## Opening a pull request

`Pierre-Sassoulas/django-survey` is the main repository, but on GitHub it is still a
fork of `ijasperyang/django-survey`. Because of that, the "Create a pull request" link
printed by `git push` and the default target of `gh pr create` point to the old
upstream. Do not use them.

Open pull requests against `main` of `Pierre-Sassoulas/django-survey` instead, with this
link (replace `<branch>` with the pushed branch name):

```
https://github.com/Pierre-Sassoulas/django-survey/compare/main...Pierre-Sassoulas:django-survey:<branch>?expand=1
```

With the GitHub CLI, name the repository and the base explicitly:

```sh
gh pr create --repo Pierre-Sassoulas/django-survey --base main --head <branch>
```
