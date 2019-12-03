SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRONTEND_APPS=("projects")

function create_path_2_assets() {
	path_2_assests="${SCRIPT_DIR}/../src/collaborative_platform/apps/${1}/assets"
	echo "$path_2_assests"
}

function build_app() {
	cd "$(create_path_2_assets $1)"
	yarn install
	yarn build
	cd "$SCRIPT_DIR"
}

function clean_libs() {
	path_2_libs="$(create_path_2_assets $1)/node_modules"
	rm -fr "$path_2_libs"
}

function build_and_clean() {
	for idx in "${FRONTEND_APPS[@]}"; do
		app=$idx
		build_app $app
		clean_libs $app
	done
}

build_and_clean