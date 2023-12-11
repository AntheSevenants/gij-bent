docker stop "gijbent_preview"
docker run --rm -p "8788:8788" --name "gijbent_preview" --mount "type=bind,src=.,target=/project/" anthesevenants/gijbent:preview