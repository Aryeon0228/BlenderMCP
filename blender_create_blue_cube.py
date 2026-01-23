"""
Blender Script: Create Blue Cube
블렌더 내부에서 직접 실행할 수 있는 스크립트입니다.

사용 방법:
1. Blender를 실행합니다
2. Scripting 탭으로 이동합니다
3. 이 스크립트를 열거나 붙여넣습니다
4. Run Script 버튼을 클릭합니다 (또는 Alt+P)
"""

import bpy
from mathutils import Vector

def create_blue_cube():
    """파란색 큐브를 생성합니다"""

    # 1. 큐브 생성
    bpy.ops.mesh.primitive_cube_add(
        size=2.0,
        location=(0, 0, 0)
    )

    # 생성된 큐브 가져오기
    cube = bpy.context.active_object
    cube.name = "BlueCube"

    print(f"✓ 큐브 생성됨: {cube.name}")

    # 2. 파란색 재질 생성 및 적용
    mat_name = "BlueMaterial"

    # 기존 재질이 있는지 확인
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        # 새 재질 생성
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True

    # Principled BSDF 노드 찾기
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")

    if principled:
        # 파란색 설정 (R=0, G=0, B=1, Alpha=1)
        principled.inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)
        print("✓ 파란색 재질 설정됨")

    # 큐브에 재질 적용
    if cube.data.materials:
        cube.data.materials[0] = mat
    else:
        cube.data.materials.append(mat)

    print("✓ 파란색 큐브 생성 완료!")

    # 뷰포트 쉐이딩 모드를 Material Preview로 변경 (색상 확인 용이)
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

    return cube

# 스크립트 실행
if __name__ == "__main__":
    print("=" * 60)
    print("파란색 큐브 생성 시작")
    print("=" * 60)

    cube = create_blue_cube()

    print("=" * 60)
    print(f"완료! 큐브 이름: {cube.name}")
    print(f"위치: {cube.location}")
    print(f"크기: {cube.scale}")
    print("=" * 60)
