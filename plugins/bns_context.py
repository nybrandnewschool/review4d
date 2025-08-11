import os
import re

import review4d

CTX_PATTERNS = [
    r"/animation/3d/(?P<folder>.*?)/(?P<parent>.*?)/(?P<name>.*?)(/|$)",
    r"/animation/(?P<folder>.*?)/(?P<parent>.*?)/(?P<name>.*?)(/|$)",
    r"/creative/(?P<folder>.*?)/(?P<parent>.*?)/(?P<name>.*?)(/|$)",
]


class BnsContextCollector(review4d.ContextCollector):
    """Extracts context related to BNS projects folder structure.

    Example:

        {
            'path': '/projects/Project/animation/3d/shots/seq/seq_010'
            'project': 'Project',
            'project_root': '/projects/Project',
            'folder': 'shots',
            'parent': 'seq',
            'name': 'seq_010',
        }
    """

    def execute(self, file, ctx):
        bns_ctx = {
            "project": "",
            "project_root": "",
            "folder": "",
            "parent": "",
            "name": "",
        }

        for pattern in CTX_PATTERNS:
            match = re.search(pattern, file, re.IGNORECASE)
            if match:
                bns_ctx.update(match.groupdict())
                project_root = file[: match.start()]
                bns_ctx["project_root"] = project_root
                bns_ctx["project"] = os.path.basename(project_root)
                break

        if not bns_ctx["project_root"]:
            bns_ctx["project_root"] = ctx["dirname"]

        ctx.update(bns_ctx)
        return ctx


def register():
    review4d.register_plugin(BnsContextCollector)
