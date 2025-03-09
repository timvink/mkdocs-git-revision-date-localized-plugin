# for testing with generated files. See mkdocs_plugin_genfiles.yml
import mkdocs_gen_files

with mkdocs_gen_files.open("foo.md", "w") as f:
    print("Bar, world!", file=f)