Guice injection for Play! framework 1.x
---------------------------------------

Edit dependencies.yml:

    require:
      - play
      - play-commons -> injection 0.1

    repositories:
      - bsbo_zip_repo:
        type: http
        artifact: https://github.com/marcoandreini/[module[/raw/master/dist/[module]-[revision].zip
        contains:
          - play-commons -> injection
