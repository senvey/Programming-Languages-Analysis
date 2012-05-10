package edu.uci.ics.inf212;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLClassLoader;

public class DynamicMenu {
	
	private static void pnt(String s, int indent) {
		StringBuilder sb = new StringBuilder(" ");
		for (int i = 0; i < indent; ++i)
			sb.append(" ");
		System.out.println(sb.toString() + s);
	}
	
	private static void pnt(String s) {
		pnt(s, 0);
	}
	
	public static String parse(String cName) {
		if (cName.startsWith("[L")) {
			int begin = cName.indexOf('L');
			int end = cName.indexOf(';');
			String type = cName.substring(begin + 1, end);
			
			int dimension = begin;
			StringBuilder sb = new StringBuilder();
			for (int i = 0; i < dimension; ++i)
				sb.append("[]");
			
			return (type + sb.toString());
		}
		return cName;
	}
	
	private static void pntClass(Class c) {
    	System.out.print(" Interfaces:");
		for (Class i : c.getInterfaces()) {
			pnt(i.getName());
		}
		System.out.print(" Super Classes:");
    	Class supc = c.getSuperclass();
    	if (supc != null)
			pnt(supc.getName());
		
		pnt("Class Info:");
		Package pkg = c.getPackage();
		if (pkg != null)
			pnt("Package: " + pkg.getName(), 2);
		
    	pnt("Constructors:", 2);
    	Constructor[] cons = c.getDeclaredConstructors();
    	for (Constructor con : cons) {
    		int mod = con.getModifiers();
    		
    		Class[] ps = con.getParameterTypes();
    		StringBuilder params = new StringBuilder();
    		for (Class p : ps) {
    			params.append(String.format("%s, ", p.getName()));
    		}
    		if (params.length() > 0)
    			params.delete(params.length() - 2, params.length());
    		
    		Class[] es = con.getExceptionTypes();
    		StringBuilder exc = new StringBuilder();
    		for (Class p : ps) {
    			exc.append(String.format("%s ", p.getName()));
    		}
    		if (exc.length() > 0)
    			params.insert(0, " throws ");
    		
    		pnt(String.format("%s %s(%s)%s;", Modifier.toString(mod),
    				con.getName(), params.toString(), exc.toString()), 4);
    	}
    	
    	pnt("Fields:", 2);
    	Field[] flds = c.getDeclaredFields();
    	for (Field fld : flds) {
    		int mod = fld.getModifiers();
    		Class type = fld.getType();
    		pnt(String.format("%s %s %s;", Modifier.toString(mod),
    				parse(type.getName()), fld.getName()), 4);
    	}
    	
    	pnt("Methods:", 2);
    	Method[] ms = c.getDeclaredMethods();
    	for (Method m : ms) {
    		int mod = m.getModifiers();
    		
    		Class[] ps = m.getParameterTypes();
    		StringBuilder params = new StringBuilder();
    		for (Class p : ps) {
    			params.append(String.format("%s, ", p.getName()));
    		}
    		if (params.length() > 0)
    			params.delete(params.length() - 2, params.length());
    		
    		Class[] es = m.getExceptionTypes();
    		StringBuilder exc = new StringBuilder();
    		for (Class p : ps) {
    			exc.append(String.format("%s ", p.getName()));
    		}
    		if (exc.length() > 0)
    			params.insert(0, " throws ");
    		
    		pnt(String.format("%s %s %s(%s);", Modifier.toString(mod),
    				parse(m.getReturnType().getName()), m.getName(),
    				params.toString()), 4);
    	}
		System.out.println();
	}
	
	private static void execute(Class c) throws InstantiationException,
			IllegalAccessException, IllegalArgumentException, InvocationTargetException {
		Object obj = c.newInstance();
    	Method[] ms = c.getDeclaredMethods();
    	
    	for (Method m : ms) {
    		Class[] ps = m.getParameterTypes();
			String[] params = new String[ps.length];
    		if (ps.length > 0) {
    			for (int i = 0; i < ps.length; ++i) {
	    	        System.out.print(String.format("Method [%s] needs a parameter of type %s: ",
	    	        		m.getName(), ps[i].getName()));
//	    	        byte[] input = new byte[16];
//	    	        try {
//						int length = System.in.read(input);
//					} catch (IOException e) {
//						// TODO Auto-generated catch block
//						e.printStackTrace();
//					}
//	    	        params[i] = input.toString();
	    	        params[i] = System.console().readLine();
    			}
    		}
    		
			Object rnt = m.invoke(obj, params);
			System.out.println(String.format("Executed method [%s].", m.getName()));
			
			if (rnt instanceof String)
				System.out.println("-- Result: " + rnt);
			
			if (rnt instanceof String[]) {
				String[] out = (String[]) rnt;
				System.out.print("-- Result: ");
				for (String s : out)
					System.out.print(s + ", ");
				System.out.println();
			}
			System.out.println();
    	}
	}
	
	private static void modifyName(Class c) throws InstantiationException,
			IllegalAccessException, SecurityException, NoSuchMethodException,
			IllegalArgumentException, InvocationTargetException {
		Object obj = c.newInstance();
		Field[] flds = c.getDeclaredFields();
		for (Field fld : flds) {
			if (fld.getName().equals("name")) {
				System.out.print(String.format("The menu name is [%s] now. Give it a new name: ",
						fld.get(obj)));
				String name = System.console().readLine();
				fld.set(obj, name);
				System.out.println(String.format("Changed the menu name to [%s].", fld.get(obj)));
			}
		}
		
		if ("Menu2".equals(c.getName())) {
			Method m = c.getMethod("toString", null);
			System.out.println(m.invoke(obj, null));
		}
	}
	
	public static void main(String[] args) throws MalformedURLException {
		URL path = DynamicMenu.class.getProtectionDomain().getCodeSource().getLocation();
        URLClassLoader loader = new URLClassLoader(new URL[] { path });
//		String path = "file:///Volumes/Private/Development/Projects/Java/Reflection/INF212-Reflection.zip";
//        URLClassLoader loader = new URLClassLoader(new URL[] { new URL(path) });
        
        System.out.print("Please enter a menu name to load [Menu1, Menu2]: ");
        String cName = System.console().readLine();
//        String cName = "Menu2";
        try {
        	Class c = loader.loadClass(cName);
        	pntClass(c);
        	execute(c);
    		modifyName(c);
		} catch (ClassNotFoundException e) {
			System.err.println(String.format("*** ERROR: Class %s cannot be found.", cName));
			e.printStackTrace();
		} catch (InstantiationException e) {
			System.err.println(String.format("*** ERROR: Cannot initiate an object for class %s.", cName));
			e.printStackTrace();
		} catch (IllegalAccessException e) {
			System.err.println(String.format("*** ERROR: Cannot initiate an object for class %s.", cName));
			e.printStackTrace();
		} catch (IllegalArgumentException e) {
			System.err.println(String.format("*** ERROR: Illegal argument while invoking methods in %s.", cName));
			e.printStackTrace();
		} catch (InvocationTargetException e) {
			System.err.println(String.format("*** ERROR: Failed to invoke methods in %s.", cName));
			e.printStackTrace();
		} catch (SecurityException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NoSuchMethodException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
