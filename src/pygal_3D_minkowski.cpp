#include "pygal.hpp"
#include <CGAL/Nef_polyhedron_3.h>
#include <CGAL/IO/Nef_polyhedron_iostream_3.h>
#include <CGAL/minkowski_sum_3.h>

typedef CGAL::Polyhedron_3<Kernel>                  Polyhedron_3;

typedef CGAL::Nef_polyhedron_3<Kernel>				Nef_polyhedron_3;

Polyhedron_3 polyhedron_minkowski_sum_3(Polyhedron_3& p, Polyhedron_3& q) {
	// convert Polyhedron to NEF
	cout << "POlyhedrons called " << endl;
	Nef_polyhedron_3 a(p);
	cout << "Converted p" << endl;
	Nef_polyhedron_3 b(q);
	cout << "Converted q" << endl;
	// cout << a << endl;
	cout << b << endl;
	Nef_polyhedron_3 summed = CGAL::minkowski_sum_3(a, b);
	cout << "SUMMED DONE" << endl;
	Polyhedron_3 result;
	summed.convert_to_polyhedron(result);
	cout << "RESULT \n\n\n\n\n" << endl;
	return result;
}

void init_3d_minkowski(py::module& m) {
	m.def("minkowski_sum_3", &polyhedron_minkowski_sum_3);
}