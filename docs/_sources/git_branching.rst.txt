Git Branching Model
===================
In this package we mostly followed `A successful Git branching model <https://nvie.com/posts/a-successful-git-branching-model/>`_ proposed by Vincent Driessen. Here are the summary of the branches:

- **master**: master branch only hosts the released software packages. Only project maintainers have write access on the master branch. 

- **develop**: develop branch is considered the main branch where the source code of HEAD always reflects a state with the latest delivered development changes for the next release.

- **supporting branch**: There are different supporting branches, three main supporting branches that we suggest the contributors to follow the naming convention includes:
    
    + **feature**: we start a new feature branch to add new features to software. The naming convention is iss[issue_number]_short_description. For example, if I need to add rotation of time series to the package and the issue number is 12, *iss12_add_rotation* can be a valid git branch name. We start it with issue number to go back and take a look at issue details if necessary. Although, feature branches are temporary, this naming convention helps developer to understand the situation while working on the codebase.

    + **hotfix**: hotfix branches will be only used for fixing a bug on a released package. After fixing the bug the third digit of the version number should be incremented by one. For example, 1.4.2 --> 1.4.3. These branches will be prefixed with hotfix and followed by upcoming version number (e.g., in this case hotfix_1.4.3)

    + **release**: Release branches support preparation of a new production release. As long as the community is not working on different releases at the same time (e.g., pre-alpha, alpha, beta, stable, and so on), we do not use release branch. 